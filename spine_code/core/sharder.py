import ast
from typing import List, Tuple, Set

class LogicSharder:
    """
    【逻辑碎片化引擎 V4】：全路径时序闭环架构。
    解决碎片化后 Return 路径导致的状态元组 UnboundLocalError。
    """
    def __init__(self, shadow_gen):
        self.shadow_gen = shadow_gen
        self.helpers = []

    def shard_function(self, func_node: ast.FunctionDef, shard_count=2) -> List[ast.AST]:
        if not isinstance(func_node, ast.FunctionDef) or len(func_node.body) < shard_count:
            return [func_node]

        # 1. 变量全集分析
        all_stored_vars = self._collect_all_stored_vars(func_node.body)
        
        # 2. 物理切割
        total_stmts = len(func_node.body)
        shard_size = max(1, total_stmts // shard_count)
        shards_bodies = []
        for i in range(0, total_stmts, shard_size):
            if len(shards_bodies) < shard_count - 1:
                shards_bodies.append(func_node.body[i:i + shard_size])
            else:
                shards_bodies.append(func_node.body[i:])
                break
        
        new_main_body = []
        # 初始化主函数作用域已知变量
        known_locals = {arg.arg for arg in func_node.args.args}
        
        # 🏛️ Preamble A：主函数变量初始化
        for v in sorted(list(all_stored_vars - {"self"})):
            new_main_body.append(ast.Assign(
                targets=[ast.Name(id=v, ctx=ast.Store())],
                value=ast.Constant(value=None)
            ))

        # 3. 碎片化迭代
        for i, body in enumerate(shards_bodies):
            loaded, stored = self._analyze_vars(body)
            shard_name = self.shadow_gen.get_or_create_mapping(f"{func_node.name}_v{i}")

            # 状态元组定义
            shard_outputs = sorted(list(stored))
            state_tuple = self._create_state_tuple(shard_outputs)

            # 输入变量分析
            relevant_inputs = loaded & known_locals
            is_method = "self" in (loaded | known_locals)
            input_vars = self._order_input_vars(relevant_inputs, is_method)
            
            # 🏛️ Preamble B：辅助函数内部预热
            helper_preamble = []
            uninitialized_in_helper = stored - (relevant_inputs | {arg.arg for arg in func_node.args.args})
            for v in sorted(list(uninitialized_in_helper - {"self"})):
                helper_preamble.append(ast.Assign(
                    targets=[ast.Name(id=v, ctx=ast.Store())],
                    value=ast.Constant(value=None)
                ))

            # 转换 Return 路径并注入预热代码
            transformer = ReturnPathTransformer(state_tuple)
            transformed_body = helper_preamble + [transformer.visit(stmt) for stmt in body]

            # 🏛️ 智能注入：只有当碎片路径未被完全覆盖（末尾没有 return）时才注入落空信号
            needs_fallback = True
            if transformed_body and isinstance(transformed_body[-1], ast.Return):
                needs_fallback = False

            if needs_fallback:
                transformed_body.append(ast.Return(value=ast.Tuple(
                    elts=[ast.Constant(value=False), ast.Constant(value=None), state_tuple],
                    ctx=ast.Load()
                )))


            helper = ast.FunctionDef(
                name=shard_name,
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg=v) for v in input_vars],
                    kwonlyargs=[], kw_defaults=[], defaults=[]
                ),
                body=transformed_body,
                decorator_list=[],
                returns=None
            )
            self.helpers.append(helper)

            # 🏛️ 调用与接力
            flag_id, val_id, state_id = f"_rf_{i}", f"_rv_{i}", f"_rs_{i}"
            new_main_body.append(self._create_call_node(shard_name, input_vars, is_method, [flag_id, val_id, state_id]))
            
            # Return 中断检查
            new_main_body.append(ast.If(
                test=ast.Name(id=flag_id, ctx=ast.Load()),
                body=[ast.Return(value=ast.Name(id=val_id, ctx=ast.Load()))],
                orelse=[]
            ))

            # 变量快照回填
            if shard_outputs:
                new_main_body.append(ast.Assign(
                    targets=[ast.Tuple(elts=[ast.Name(id=v, ctx=ast.Store()) for v in shard_outputs], ctx=ast.Store())],
                    value=ast.Name(id=state_id, ctx=ast.Load())
                ))
            
            known_locals.update(stored)

        func_node.body = new_main_body
        res = self.helpers + [func_node]
        for node in res: ast.fix_missing_locations(node)
        return res

    def _collect_all_stored_vars(self, body: List[ast.stmt]) -> Set[str]:
        stored = set()
        for stmt in body:
            for node in ast.walk(stmt):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    stored.add(node.id)
        return stored

    def _analyze_vars(self, body: List[ast.stmt]) -> Tuple[Set[str], Set[str]]:
        loaded, stored = set(), set()
        for stmt in body:
            if isinstance(stmt, ast.AugAssign):
                if isinstance(stmt.target, ast.Name):
                    loaded.add(stmt.target.id)
                    stored.add(stmt.target.id)
            for node in ast.walk(stmt):
                if isinstance(node, ast.Name):
                    if isinstance(node.ctx, ast.Load): loaded.add(node.id)
                    elif isinstance(node.ctx, ast.Store): stored.add(node.id)
                elif isinstance(node, ast.Attribute):
                    curr = node.value
                    while isinstance(curr, ast.Attribute): curr = curr.value
                    if isinstance(curr, ast.Name): loaded.add(curr.id)
                elif isinstance(node, (ast.For, ast.With)):
                    # For 循环和 With 语句的 target 是 Store
                    if isinstance(node, ast.For):
                        for t_node in ast.walk(node.target):
                            if isinstance(t_node, ast.Name): stored.add(t_node.id)
                    else:
                        # With 语句：处理 with open(...) as f
                        for item in node.items:
                            if item.optional_vars:
                                for t_node in ast.walk(item.optional_vars):
                                    if isinstance(t_node, ast.Name): stored.add(t_node.id)
        return loaded, stored

    def _order_input_vars(self, vars_set: Set[str], is_method: bool) -> List[str]:
        others = sorted(list(vars_set - {"self"}))
        return (["self"] if is_method else []) + others

    def _create_state_tuple(self, var_names: List[str]) -> ast.Tuple:
        return ast.Tuple(elts=[ast.Name(id=v, ctx=ast.Load()) for v in var_names], ctx=ast.Load())

    def _create_call_node(self, name: str, inputs: List[str], is_method: bool, target_ids: List[str]) -> ast.Assign:
        if is_method:
            func_target = ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr=name, ctx=ast.Load())
            args = [ast.Name(id=v, ctx=ast.Load()) for v in inputs if v != "self"]
        else:
            func_target = ast.Name(id=name, ctx=ast.Load())
            args = [ast.Name(id=v, ctx=ast.Load()) for v in inputs]
        return ast.Assign(
            targets=[ast.Tuple(elts=[ast.Name(id=tid, ctx=ast.Store()) for tid in target_ids], ctx=ast.Store())],
            value=ast.Call(func=func_target, args=args, keywords=[])
        )

class ReturnPathTransformer(ast.NodeTransformer):
    def __init__(self, state_tuple):
        self.state_tuple = state_tuple

    def visit_Return(self, node):
        return ast.Return(value=ast.Tuple(
            elts=[ast.Constant(value=True), node.value or ast.Constant(value=None), self.state_tuple],
            ctx=ast.Load()
        ))

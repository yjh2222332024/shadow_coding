"""
Shadow_Coding - AI 代码隐私保护网关
Copyright (C) 2026 严俊皓 <2857922968@qq.com>

基于 AGPLv3 许可证开源
https://github.com/yjh2222332024/Shadow_Coding
"""

import ast
import hashlib
from typing import List, Tuple, Set, Union

class LogicSharder:
    """
    【逻辑碎片化引擎 V4】：全路径时序闭环架构。
    V3.2 增强：支持递归复杂度计算与全量符号预脱敏。
    """
    def __init__(self, shadow_gen):
        self.shadow_gen = shadow_gen
        self.helpers = []

    def _is_sensitive_ast(self, body: List[ast.stmt]) -> bool:
        """基于 AST 结构的模式识别"""
        for stmt in body:
            for node in ast.walk(stmt):
                if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mult, ast.Sub)):
                    return True
                if isinstance(node, ast.Compare):
                    return True
                if isinstance(node, ast.Name) and any(kw in node.id.lower() for kw in ['price', 'auth', 'secret', 'key', 'balance', 'token']):
                    return True
        return False

    def _extract_all_symbols(self, func_node: ast.AST):
        """
        【V3.2 关键补丁】：递归提取所有符号到映射表，确保即便不碎片化也能影子化。
        """
        # 1. 提取函数参数
        if isinstance(func_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in func_node.args.args:
                self.shadow_gen.get_or_create_mapping(arg.arg)

        # 2. 遍历所有子节点提取变量名、函数名等
        for node in ast.walk(func_node):
            if isinstance(node, ast.Name):
                # 排除内置关键字
                if node.id not in ['True', 'False', 'None', 'self', 'cls']:
                    self.shadow_gen.get_or_create_mapping(node.id)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.shadow_gen.get_or_create_mapping(node.name)

    def _calculate_body_complexity(self, body: List[ast.stmt]) -> int:
        """
        【V3.2 深度探测】：递归计算逻辑复杂度，穿透 Try/If/For 等容器。
        """
        complexity = 0
        for stmt in body:
            if isinstance(stmt, ast.Try):
                complexity += self._calculate_body_complexity(stmt.body)
                for handler in stmt.handlers:
                    complexity += self._calculate_body_complexity(handler.body)
                complexity += self._calculate_body_complexity(stmt.finalbody)
            elif isinstance(stmt, (ast.For, ast.While, ast.AsyncFor)):
                complexity += 1 # 循环本身
                complexity += self._calculate_body_complexity(stmt.body)
                complexity += self._calculate_body_complexity(stmt.orelse)
            elif isinstance(stmt, ast.If):
                complexity += 1 # 分支本身
                complexity += self._calculate_body_complexity(stmt.body)
                complexity += self._calculate_body_complexity(stmt.orelse)
            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # 嵌套定义视为高复杂度
                complexity += 5
            else:
                # 普通赋值、调用等
                complexity += 1
        return complexity

    def shard_function(self, func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef], shard_count=2) -> List[ast.AST]:
        # ✅ 第一步：强制全量符号提取（无论是否碎片化，变量名必须变）
        self._extract_all_symbols(func_node)

        # ✅ 第二步：深度复杂度判定
        if not isinstance(func_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return [func_node]

        body_complexity = self._calculate_body_complexity(func_node.body)
        
        # 如果复杂度不足，或者是一个极简函数，跳过碎片化但保留影子化
        if body_complexity < shard_count or len(func_node.body) < 1:
            return [func_node]

        is_async = isinstance(func_node, ast.AsyncFunctionDef)
        all_stored_vars = self._collect_all_stored_vars(func_node.body)
        
        # 3. 物理切割 (对于只有一个大容器的情况，我们需要尝试切割容器内部，或者至少保持整体)
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
        known_locals = {arg.arg for arg in func_node.args.args}
        
        # Preamble A：变量初始化
        for v in sorted(list(all_stored_vars - {"self"})):
            new_main_body.append(ast.Assign(
                targets=[ast.Name(id=v, ctx=ast.Store())],
                value=ast.Constant(value=None)
            ))

        # 4. 碎片化迭代
        for i, body in enumerate(shards_bodies):
            loaded, stored = self._analyze_vars(body)
            shard_name = self.shadow_gen.get_or_create_mapping(f"{func_node.name}_v{i}")

            shard_outputs = sorted(list(stored))
            state_tuple = self._create_state_tuple(shard_outputs)

            relevant_inputs = loaded & known_locals
            is_method = "self" in (loaded | known_locals)
            input_vars = self._order_input_vars(relevant_inputs, is_method)
            
            helper_preamble = []
            uninitialized_in_helper = stored - (relevant_inputs | {arg.arg for arg in func_node.args.args})
            for v in sorted(list(uninitialized_in_helper - {"self"})):
                helper_preamble.append(ast.Assign(
                    targets=[ast.Name(id=v, ctx=ast.Store())],
                    value=ast.Constant(value=None)
                ))

            transformer = ReturnPathTransformer(state_tuple)
            transformed_body = helper_preamble + [transformer.visit(stmt) for stmt in body]

            needs_fallback = True
            if transformed_body and isinstance(transformed_body[-1], ast.Return):
                needs_fallback = False

            if needs_fallback:
                transformed_body.append(ast.Return(value=ast.Tuple(
                    elts=[ast.Constant(value=False), ast.Constant(value=None), state_tuple],
                    ctx=ast.Load()
                )))

            # 创建辅助函数（保持 Async 属性）
            helper_cls = ast.AsyncFunctionDef if is_async else ast.FunctionDef
            helper = helper_cls(
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

            # 调用与接力 (Async 调用需 await)
            flag_id, val_id, state_id = f"_rf_{i}", f"_rv_{i}", f"_rs_{i}"
            new_main_body.append(self._create_call_node(shard_name, input_vars, is_method, [flag_id, val_id, state_id], is_async))
            
            new_main_body.append(ast.If(
                test=ast.Name(id=flag_id, ctx=ast.Load()),
                body=[ast.Return(value=ast.Name(id=val_id, ctx=ast.Load()))],
                orelse=[]
            ))

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
                elif isinstance(node, (ast.For, ast.With, ast.AsyncFor)):
                    if isinstance(node, (ast.For, ast.AsyncFor)):
                        for t_node in ast.walk(node.target):
                            if isinstance(t_node, ast.Name): stored.add(t_node.id)
                    else:
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

    def _create_call_node(self, name: str, inputs: List[str], is_method: bool, target_ids: List[str], is_async: bool) -> ast.Assign:
        if is_method:
            func_target = ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()), attr=name, ctx=ast.Load())
            args = [ast.Name(id=v, ctx=ast.Load()) for v in inputs if v != "self"]
        else:
            func_target = ast.Name(id=name, ctx=ast.Load())
            args = [ast.Name(id=v, ctx=ast.Load()) for v in inputs]
        
        call_node = ast.Call(func=func_target, args=args, keywords=[])
        if is_async:
            call_node = ast.Await(value=call_node)
            
        return ast.Assign(
            targets=[ast.Tuple(elts=[ast.Name(id=tid, ctx=ast.Store()) for tid in target_ids], ctx=ast.Store())],
            value=call_node
        )

class ReturnPathTransformer(ast.NodeTransformer):
    def __init__(self, state_tuple):
        self.state_tuple = state_tuple

    def visit_Return(self, node):
        return ast.Return(value=ast.Tuple(
            elts=[ast.Constant(value=True), node.value or ast.Constant(value=None), self.state_tuple],
            ctx=ast.Load()
        ))

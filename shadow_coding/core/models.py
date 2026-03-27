"""
Shadow_Coding - AI 代码隐私保护网关
Copyright (C) 2026 严俊皓 <2857922968@qq.com>

基于 AGPLv3 许可证开源
https://github.com/yjh2222332024/Shadow_Coding
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum
import uuid

class NodeStatus(str, Enum):
    COLLAPSED = "collapsed"
    EXPANDED = "expanded"
    LOADED = "loaded"

class NodeType(str, Enum):
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    MODULE = "module"

class ParamSignature(BaseModel):
    name: str
    type: Optional[str] = None
    default: Optional[str] = None

class ContractCondition(BaseModel):
    type: Literal["pre", "post", "raises", "side_effect"]
    description: str

class MethodInfo(BaseModel):
    real_name: str
    shadow_name: str
    params: List[ParamSignature]
    returns: str = "Any"
    conditions: List[ContractCondition] = []
    doc_summary: str = ""

class ShadowContract(BaseModel):
    """
    【L2 行为契约】：给 AI 看的影子桩。
    """
    source_file: str
    source_hash: str
    shadow_name: str
    original_name: str
    node_type: Literal["class", "function"]
    methods: List[MethodInfo] = [] # 强类型化
    conditions: List[ContractCondition] = []

class SpineNode(BaseModel):
    # UUID 增加至 12 位以降低碰撞率
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    t: str = Field(..., alias="title")
    lv: int = Field(..., alias="level")
    lines: List[int] = Field(..., alias="line_range")
    type: NodeType = Field(default=NodeType.FUNCTION)
    sum: Optional[str] = Field(None, alias="summary")
    children: List['SpineNode'] = []
    sn: Optional[str] = Field(None, alias="shadow_name")
    status: NodeStatus = NodeStatus.COLLAPSED

class SpineProtocol(BaseModel):
    version: str = "SEC-CODE-2.0"
    project_id: str
    file_hash: str
    spine: List[SpineNode]
    mapping: Dict[str, str] = Field(default_factory=dict)
    contracts: Dict[str, ShadowContract] = Field(default_factory=dict)
    
    def get_node_by_id(self, node_id: str, nodes: Optional[List[SpineNode]] = None) -> Optional[SpineNode]:
        search_list = nodes if nodes is not None else self.spine
        for node in search_list:
            if node.id == node_id:
                return node
            if node.children:
                res = self.get_node_by_id(node_id, node.children)
                if res: return res
        return None

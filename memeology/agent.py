from typing import List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from memeology.llm import LLMEngine
from memeology.vector_store import WeaviateStore


class AgentState(BaseModel):
    """代理状态"""

    messages: List[Dict[str, str]]
    current_query: str
    filters: Dict[str, Any]
    search_results: Optional[List[Dict[str, Any]]] = None
    clarification_needed: bool = False


class MemeologyAgent:
    def __init__(self):
        """初始化 Memeology 代理"""
        self.llm = LLMEngine()
        self.vector_store = WeaviateStore()
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> StateGraph:
        """创建代理工作流"""
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("process_query", self._process_query)
        workflow.add_node("search_memes", self._search_memes)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("need_clarification", self._need_clarification)

        # 设置边
        workflow.add_edge("process_query", "search_memes")
        workflow.add_edge("search_memes", "generate_response")
        workflow.add_edge("process_query", "need_clarification")
        workflow.add_edge("need_clarification", END)
        workflow.add_edge("generate_response", END)

        # 设置条件
        workflow.set_entry_point("process_query")

        return workflow.compile()

    def _process_query(self, state: AgentState) -> AgentState:
        """处理用户查询"""
        # 使用 LLM 分析查询意图
        intent = self.llm.analyze_intent(state.current_query)
        state.filters.update(intent.get("filters", {}))
        return state

    def _search_memes(self, state: AgentState) -> AgentState:
        """搜索相关梗图"""
        results = self.vector_store.search(
            query=state.current_query, filters=state.filters
        )
        state.search_results = results
        return state

    def _generate_response(self, state: AgentState) -> AgentState:
        """生成响应"""
        response = self.llm.generate_response(
            query=state.current_query,
            results=state.search_results,
            history=state.messages,
        )
        state.messages.append({"role": "assistant", "content": response})
        return state

    def _need_clarification(self, state: AgentState) -> AgentState:
        """请求澄清"""
        clarification = self.llm.generate_clarification(state.current_query)
        state.messages.append({"role": "assistant", "content": clarification})
        state.clarification_needed = True
        return state

    def process_message(self, message: str, history: List[List[str]]) -> str:
        """处理用户消息"""
        # 转换历史记录格式
        messages = []
        for human, assistant in history:
            messages.extend(
                [
                    {"role": "user", "content": human},
                    {"role": "assistant", "content": assistant},
                ]
            )

        # 创建初始状态
        state = AgentState(messages=messages, current_query=message, filters={})

        # 运行工作流
        final_state = self.workflow.invoke(state)

        # 返回最后一条助手消息
        return final_state.messages[-1]["content"]

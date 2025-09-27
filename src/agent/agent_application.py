from langgraph.graph.state import CompiledStateGraph

from src.agent.chat_agent_application import ChatAgentApplicationFactory, ChatAgentApplication, \
    DefaultChatAgentApplicationFactory
from src.graph.graph_provider import GraphProvider
from src.state.type import GRAPH_STATE, MESSAGE_DTO


class AgentApplication:

    @classmethod
    def initialize(cls, graph: GraphProvider[GRAPH_STATE]| CompiledStateGraph[GRAPH_STATE],
                   chat_agent_factory: ChatAgentApplicationFactory[GRAPH_STATE, MESSAGE_DTO] = None
                   ) -> ChatAgentApplication:
        if chat_agent_factory is None:
            return DefaultChatAgentApplicationFactory().create(graph=graph)
        else:
            chat_agent_factory.create(graph=graph)

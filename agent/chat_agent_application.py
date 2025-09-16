from abc import ABC, abstractmethod
from typing import Generic, Any

from langgraph.graph.state import CompiledStateGraph
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import ChatAgentMessage, ChatContext, ChatAgentResponse

from graph.graph_provider import GraphProvider
from state.mapper import StateMapper, DefaultStateMapper
from state.type import GRAPH_STATE, MESSAGE_DTO, DefaultState


class ChatAgentApplication(ABC, ChatAgent, Generic[GRAPH_STATE, MESSAGE_DTO]):
    def __init__(self,
                 graph: CompiledStateGraph[GRAPH_STATE] | GraphProvider[GRAPH_STATE],
                 mapper: StateMapper[GRAPH_STATE, MESSAGE_DTO]):
        self.mapper = mapper
        self.graph = graph


class DefaultChatAgentApplication(ChatAgentApplication[DefaultState, list[ChatAgentMessage]]):

    def predict(self, messages: list[ChatAgentMessage], context: ChatContext | None = None,
                custom_inputs: dict[str, Any] | None = None) -> ChatAgentResponse:
        input_state = self.mapper.map_from_message_to_state(messages)
        if isinstance(self.graph, GraphProvider):
            graph = self.graph.provide()
        else:
            graph = self.graph
        state = graph.invoke(input_state)
        result = self.mapper.map_from_state_to_message(state)
        return ChatAgentResponse(messages=result)


class ChatAgentApplicationFactory(ABC, Generic[GRAPH_STATE, MESSAGE_DTO]):

    @abstractmethod
    def create(self, graph: GraphProvider[GRAPH_STATE] | CompiledStateGraph[GRAPH_STATE]):
        pass


class DefaultChatAgentApplicationFactory(ChatAgentApplicationFactory[DefaultState, list[ChatAgentMessage]]):
    def create(self, graph: GraphProvider[GRAPH_STATE] | CompiledStateGraph[GRAPH_STATE]):
        mapper: StateMapper[DefaultState, list[ChatAgentMessage]] = DefaultStateMapper()
        return DefaultChatAgentApplication(graph=graph, mapper=mapper)

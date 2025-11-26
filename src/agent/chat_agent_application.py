from abc import ABC, abstractmethod
from typing import Generic, Any, Union, Generator

from langgraph.graph.state import CompiledStateGraph
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import (
    ChatAgentMessage,
    ChatContext,
    ChatAgentResponse,
    ChatAgentChunk,
)

from src.graph.graph_provider import GraphProvider
from src.state.mapper import StateMapper, DefaultStateMapper
from src.state.type import GRAPH_STATE, MESSAGE_DTO, DefaultState
import logging
import uuid


class ChatAgentApplication(ABC, ChatAgent, Generic[GRAPH_STATE, MESSAGE_DTO]):
    def __init__(
        self,
        graph: Union[CompiledStateGraph, GraphProvider],
        mapper: StateMapper[GRAPH_STATE, MESSAGE_DTO],
    ):
        self.mapper = mapper
        self.graph = graph


class DefaultChatAgentApplication(
    ChatAgentApplication[DefaultState, list[ChatAgentMessage]]
):

    def predict_stream(
        self,
        messages: list[ChatAgentMessage],
        context: ChatContext | None = None,
        custom_inputs: dict[str, Any] | None = None,
    ) -> Generator[ChatAgentChunk, None, None]:
        logging.warning("hey in predict stream function")

        input_state = self.mapper.map_from_message_to_state(messages)
        if isinstance(self.graph, GraphProvider):
            graph = self.graph.provide(self.config_yaml)
        else:
            graph = self.graph

        config = {}
        if custom_inputs:
            config.update(custom_inputs)

        try:
            for event in graph.stream(
                    input_state, config=config, stream_mode=["custom", "updates"]
            ):
                # Handle updates mode - progress messages
                if event[0] == "updates":
                    logging.warning("Update events")

                # Handle custom mode - final answer chunks
                elif event[0] == "custom":
                    if event[1].get("type") == "final_answer_chunk":
                        yield ChatAgentChunk(
                            delta=ChatAgentMessage(
                                role="assistant",
                                content=event[1].get("content", ""),
                                id=event[1].get("id"),
                            )
                        )
        except Exception as e:
            logging.error(f"Error in predict_stream: {e}")
            # Yield error message as a chunk
            yield ChatAgentChunk(
                delta=ChatAgentMessage(
                    role="assistant",
                    content="Agent is encountering some weird signal -.- Please try again after a little moment.",
                    id=str(uuid.uuid4()),
                )
            )

    def predict(
        self,
        messages: list[ChatAgentMessage],
        context: ChatContext | None = None,
        custom_inputs: dict[str, Any] | None = None,
    ) -> ChatAgentResponse:
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
    def create(
        self, graph: GraphProvider[GRAPH_STATE] | CompiledStateGraph[GRAPH_STATE]
    ):
        pass


class DefaultChatAgentApplicationFactory(
    ChatAgentApplicationFactory[DefaultState, list[ChatAgentMessage]]
):
    def create(
        self, graph: GraphProvider[GRAPH_STATE] | CompiledStateGraph[GRAPH_STATE]
    ):
        mapper: StateMapper[DefaultState, list[ChatAgentMessage]] = DefaultStateMapper()
        return DefaultChatAgentApplication(graph=graph, mapper=mapper)

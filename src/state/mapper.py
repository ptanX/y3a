import uuid
from abc import ABC, abstractmethod
from typing import Generic

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from mlflow.types.agent import ChatAgentMessage

from src.state.type import GRAPH_STATE, MESSAGE_DTO, DefaultState


class StateMapper(ABC, Generic[GRAPH_STATE, MESSAGE_DTO]):

    @abstractmethod
    def map_from_state_to_message(self, state: GRAPH_STATE) -> MESSAGE_DTO:
        pass

    @abstractmethod
    def map_from_message_to_state(self, message: MESSAGE_DTO) -> GRAPH_STATE:
        pass


def convert_to_mlflow_message(message) -> ChatAgentMessage:
    if isinstance(message, AIMessage):
        return ChatAgentMessage(
            role="assistant", content=message.content, id=message.id
        )
    elif isinstance(message, HumanMessage):
        return ChatAgentMessage(role="user", content=message.content, id=message.id)
    elif isinstance(message, SystemMessage):
        return ChatAgentMessage(role="system", content=message.content, id=message.id)


class DefaultStateMapper(StateMapper[DefaultState, list[ChatAgentMessage]]):

    def map_from_state_to_message(self, state: DefaultState) -> list[ChatAgentMessage]:
        message = state.get("message", "")
        content = ""
        if isinstance(message, str):
            content = message
        elif isinstance(message, AIMessage):
            content = message.content
        result = [
            ChatAgentMessage(role="assistant", content=content, id=str(uuid.uuid4()))
        ]
        return result

    def map_from_message_to_state(
        self, message: list[ChatAgentMessage]
    ) -> DefaultState:
        actual_message = message[-1].content
        return {"message": HumanMessage(content=actual_message)}

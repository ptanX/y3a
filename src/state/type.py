from typing import TypeVar, TypedDict, Annotated, List

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

GRAPH_STATE = TypeVar('GRAPH_STATE', bound=TypedDict)
MESSAGE_DTO = TypeVar('MESSAGE_DTO')


class DefaultState(TypedDict):
    message: BaseMessage

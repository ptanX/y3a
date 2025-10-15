from typing import TypeVar, TypedDict

from langchain_core.messages import BaseMessage

GRAPH_STATE = TypeVar('GRAPH_STATE', bound=TypedDict)
MESSAGE_DTO = TypeVar('MESSAGE_DTO')
EXECUTION_INPUT = TypeVar('EXECUTION_INPUT', bound=object)


class DefaultState(TypedDict):
    message: BaseMessage

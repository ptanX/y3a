from abc import ABC, abstractmethod
from typing import Generic

from langgraph.graph.state import CompiledStateGraph

from src.state.type import GRAPH_STATE


class GraphProvider(ABC, Generic[GRAPH_STATE]):

    @abstractmethod
    def provide(self) -> CompiledStateGraph[GRAPH_STATE]:
        pass

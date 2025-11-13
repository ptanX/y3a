from abc import ABC, abstractmethod
from typing import List

from src.lending.agent.lending_agent_model import LendingShortTermContext


class ShortTermContextRepository(ABC):

    @abstractmethod
    def put(self, thread_id: str, context: LendingShortTermContext):
        pass

    @abstractmethod
    def get(self, thread_id: str) -> List[LendingShortTermContext]:
        pass


class InMemoryShortTermContextRepository(ShortTermContextRepository):

    def __init__(self, initialized_memory=None):
        if initialized_memory is None:
            initialized_memory = {}
        self.memory = initialized_memory

    def put(self, thread_id: str, context: LendingShortTermContext):
        self.memory[thread_id] = [context]

    def get(self, thread_id: str) -> List[LendingShortTermContext]:
        context = self.memory.get(thread_id)
        if context is None:
            return []
        else:
            return context

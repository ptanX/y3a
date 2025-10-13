import asyncio
from abc import ABC, abstractmethod
from typing import Generic, Dict, List, Any

from src.state.type import EXECUTION_INPUT


class ExecutionInput:

    def __init__(self, handler_name, handler_input):
        self.handler_name = handler_name
        self.handler_input = handler_input


class ExecutionHandler(ABC, Generic[EXECUTION_INPUT]):

    @abstractmethod
    async def handle(self, execution_input: EXECUTION_INPUT) -> Dict:
        pass


class ExecutionDispatcherBuilder:

    def __init__(self):
        self.execution_dispatcher = ExecutionDispatcher()

    def set_dispatcher(self, name: str, handler: ExecutionHandler):
        self.execution_dispatcher.dispatchers[name] = handler
        return self

    def build(self):
        return self.execution_dispatcher


class TestExecutionHandler(ExecutionHandler[str]):

    async def handle(self, execution_input: str) -> Dict:
        return {execution_input: execution_input}


class ExecutionDispatcher:

    def __init__(self):
        self.dispatchers: Dict[str, ExecutionHandler] = {}

    async def dispatch(self, list_inputs: List[ExecutionInput]) -> Dict[str, Any]:
        tasks = {}

        for execution_input in list_inputs:
            handler = self.dispatchers.get(execution_input.handler_name)
            if handler:
                tasks[execution_input.handler_name] = handler.handle(execution_input.handler_input)
            else:
                print(f"Warning: No handler found for '{execution_input.handler_name}'")

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        return {key: result for key, result in zip(tasks.keys(), results)}

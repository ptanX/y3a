import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any


class ExecutionInput:

    def __init__(self, handler_name, handler_input):
        self.handler_name = handler_name
        self.handler_input = handler_input


class ExecutionOutput:
    def __init__(self, handler_name, handler_output):
        self.handler_name = handler_name
        self.handler_output = handler_output


class ExecutionHandler(ABC):

    @abstractmethod
    async def handle(self, execution_input: ExecutionInput) -> ExecutionOutput:
        pass


class ExecutionDispatcherBuilder:

    def __init__(self):
        self.execution_dispatcher = ExecutionDispatcher()

    def set_dispatcher(self, name: str, handler: ExecutionHandler):
        self.execution_dispatcher.dispatchers[name] = handler
        return self

    def build(self):
        return self.execution_dispatcher


class TestExecutionHandler(ExecutionHandler):

    async def handle(self, execution_input: ExecutionInput) -> ExecutionOutput:
        return ExecutionOutput(
            handler_name=execution_input.handler_name,
            handler_output=execution_input.handler_input,
        )


class ExecutionDispatcher:

    def __init__(self):
        self.dispatchers: Dict[str, ExecutionHandler] = {}

    async def dispatch(self, list_inputs: List[ExecutionInput]) -> List[Dict[str, Any]]:
        """
        Returns list of results in the same order as inputs.
        """
        # Create tasks as a list (preserves order)
        tasks = [
            self._execute_single(execution_input)
            for execution_input in list_inputs
        ]

        # Execute all concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Format results
        return [
            {
                'handler_name': result.handler_name,
                'output': result if not isinstance(result, Exception) else None
            }
            for i, result in enumerate(results)
        ]

    async def _execute_single(self, execution_input: ExecutionInput) -> Any:
        """Execute a single handler."""
        handler = self.dispatchers.get(execution_input.handler_name)

        if not handler:
            raise ValueError(f"No handler found for '{execution_input.handler_name}'")

        return await handler.handle(execution_input.handler_input)

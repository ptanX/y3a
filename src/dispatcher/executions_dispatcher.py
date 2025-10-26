import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List


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

    async def dispatch(self, list_inputs: List[ExecutionInput]) -> List[ExecutionOutput]:
        """
        Returns list of results in the same order as inputs.
        """
        # Create tasks as a list (preserves order)
        tasks = [
            self._execute_single(execution_input)
            for execution_input in list_inputs
        ]

        # Execute all concurrently
        results = await asyncio.gather(*tasks)

        # Format results
        formatted_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Convert exception to ExecutionOutput
                raise ValueError(f"output error for '{str(result)}'")
            else:
                # Already an ExecutionOutput
                formatted_results.append(result)

        return formatted_results

    async def _execute_single(self, execution_input: ExecutionInput) -> ExecutionOutput:
        """Execute a single handler."""
        handler = self.dispatchers.get(execution_input.handler_name)

        if not handler:
            raise ValueError(f"No handler found for '{execution_input.handler_name}'")

        result = await handler.handle(execution_input.handler_input)
        if isinstance(result, ExecutionOutput):
            return result
        else:
            raise ValueError(f"output error for '{execution_input.handler_name}'")

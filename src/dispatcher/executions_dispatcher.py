import asyncio
from typing import Dict, List, Callable, Awaitable


class ExecutionInput:

    def __init__(self, handler_name, execution_id, input_content):
        self.handler_name = handler_name
        self.execution_id = execution_id
        self.input_content = input_content


class ExecutionOutput:
    def __init__(self, handler_name, execution_id, output_content):
        self.handler_name = handler_name
        self.execution_id = execution_id
        self.output_content = output_content


ExecutionHandler = Callable[[ExecutionInput], Awaitable[ExecutionOutput]]


class ExecutionDispatcherBuilder:

    def __init__(self):
        self.execution_dispatcher = ExecutionDispatcher()

    def set_dispatcher(self, name: str, handler: ExecutionHandler):
        self.execution_dispatcher.dispatchers[name] = handler
        return self

    def build(self):
        return self.execution_dispatcher


async def handle_simple_execution(execution_input: ExecutionInput) -> ExecutionOutput:
    return ExecutionOutput(
        handler_name=execution_input.handler_name,
        execution_id=execution_input.execution_id,
        output_content=execution_input.input_content
    )


class ExecutionDispatcher:
    def __init__(self):
        self.dispatchers: Dict[str, ExecutionHandler] = {}

    async def dispatch(
        self, list_inputs: List[ExecutionInput]
    ) -> List[ExecutionOutput]:
        """
        Returns list of results of execution input.
        """
        tasks = [
            self._execute_single(execution_input) for execution_input in list_inputs
        ]
        results: List[ExecutionOutput | Exception] = list(
            await asyncio.gather(*tasks, return_exceptions=True)
        )
        formatted_results: List[ExecutionOutput] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                raise ValueError(f"output error for '{str(result)}'")
            formatted_results.append(result)
        return formatted_results

    async def _execute_single(self, execution_input: ExecutionInput) -> ExecutionOutput:
        handler = self.dispatchers.get(execution_input.handler_name)
        if not handler:
            raise ValueError(f"No handler found for '{execution_input.handler_name}'")

        result = await handler(execution_input)
        if isinstance(result, ExecutionOutput):
            return result
        raise ValueError(f"output error for '{execution_input.handler_name}'")
    
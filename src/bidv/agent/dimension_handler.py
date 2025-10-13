from typing import Dict

from src.graph.node_executions_dispatcher import ExecutionHandler
from src.state.type import EXECUTION_INPUT


class CapitalHandler(ExecutionHandler):

    async def handle(self, execution_input: EXECUTION_INPUT) -> Dict:
        return {}


class AssetHandler(ExecutionHandler):
    async def handle(self, execution_input: EXECUTION_INPUT) -> Dict:
        return {}


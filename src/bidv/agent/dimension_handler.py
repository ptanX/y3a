from typing import Dict

from src.dispatcher.executions_dispatcher import ExecutionHandler


class CapitalHandler(ExecutionHandler[Dict]):

    async def handle(self, execution_input: Dict) -> Dict:
        return {}


class AssetHandler(ExecutionHandler):
    async def handle(self, execution_input: Dict) -> Dict:
        return {}


class ManagementHandler(ExecutionHandler):
    async def handle(self, execution_input: Dict) -> Dict:
        return {}


class EarningHandler(ExecutionHandler):
    async def handle(self, execution_input: Dict) -> Dict:
        return {}


class LiquidityHandler(ExecutionHandler):
    async def handle(self, execution_input: Dict) -> Dict:
        return {}

import uuid
from typing import Any, Optional

import mlflow
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import ChatAgentMessage, ChatAgentResponse, ChatContext


class BasicChatAgent(ChatAgent):

    @mlflow.trace(name="Agent Call")
    def _call_agent(
        self, message: ChatAgentMessage, role: str, params: Optional[dict] = None
    ):
        pass

    @mlflow.trace(name="Predict")
    def predict(self, messages: list[ChatAgentMessage], context: ChatContext | None = None,
                custom_inputs: dict[str, Any] | None = None) -> ChatAgentResponse:
        id = str(uuid.uuid4())
        self._call_agent(messages[0], "user")
        result = [ChatAgentMessage(
                role="assistant", content="Hello my name is new agent", id=id
            )]
        return ChatAgentResponse(messages=result)

## TODO implement the chain here
from typing import Iterable
from pydantic import BaseModel
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionMessageFunctionToolCall,
    ChatCompletionToolParam
)

class ModelArguments(BaseModel):
    model: str
    stream: bool
    tools: list[ChatCompletionToolParam]
    tool_choice: str
    # messages: list[ChatCompletionMessageParam]
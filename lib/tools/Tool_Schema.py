from datetime import tzinfo
from typing import Callable
from enum import Enum

from pydantic import BaseModel
from lib.tools import Tool_Functions
from openai.types.chat import (
    ChatCompletionToolParam
)

class FunctionType(Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"

class Execution(Enum):
    SYNCHRONOUS = "sync"
    ASYNCHRONOUS = "async"

class Tool(Enum):
    get_local_time = "get_local_time"

class FunctionToolSchema(BaseModel):
    fPtr: Callable
    execution: Execution
    type: FunctionType
    # args: dict[object, object]

tool_registry = {
    Tool.get_local_time.value: FunctionToolSchema(
        fPtr=Tool_Functions.get_local_time,
        execution=Execution.SYNCHRONOUS,
        type=FunctionType.STATIC,
        # args={"format": str, "timezone": tzinfo}
    )
}

tools: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "get_local_time",
            "description": "Get the current local time. Only use this when the user explicitly asks for the time, current time, what time it is, or needs to know the time for scheduling purposes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Why the user needs to know the time (e.g., 'user asked what time it is', 'user wants to schedule something')",
                    },
                    "timezone": {
                        "type": "string",
                        "description": "The timezone the time will be returned from; must be in IANA zone format.",
                        "default": "UTC"
                    },
                    "format": {
                        "type": "string",
                        "description": "The format (python-strftime) the time will be returned in.",
                        "default": "%H:%M",
                    }
                },
                "required": ["reason"],
                "additionalProperties": False
            },
            "strict": True,
        }
    }
]
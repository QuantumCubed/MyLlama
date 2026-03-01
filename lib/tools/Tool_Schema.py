from typing import Callable
from enum import Enum

from pydantic import BaseModel
from lib.tools.Tool_Functions import ExternalTools

# class FunctionType(Enum):
#     STATIC = "static"
#     DYNAMIC = "dynamic"

class Execution(Enum):
    SYNCHRONOUS = 0
    ASYNCHRONOUS = 1

class Tool(BaseModel):
    fn_ptr: Callable
    execution: Execution
    direct_return: bool

    async def execute(self, **kwargs) -> str:
        if self.execution == Execution.SYNCHRONOUS:
            return self.fn_ptr(**kwargs)
        return await self.fn_ptr(**kwargs)
    
ToolRegistry = {
    "time_now": Tool(
        fn_ptr=ExternalTools.time_now,
        execution=Execution.SYNCHRONOUS,
        direct_return=True
    ),
    "standup_lamp_toggle": Tool(
        fn_ptr=ExternalTools.standup_lamp_toggle,
        execution=Execution.ASYNCHRONOUS,
        direct_return=False
    )
}

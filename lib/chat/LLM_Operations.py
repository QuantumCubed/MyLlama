import json
import os
from pydantic import TypeAdapter, ValidationError
from typing import Sequence, cast
from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionMessageFunctionToolCall
)
from lib.chat.ChatSchemas import ModelArguments
from lib.tools import Tool_Schema
from lib.utils import string_utils

class LLM_OPS:
    def __init__(self) -> None:
        self.OllamaClient: AsyncOpenAI = AsyncOpenAI(base_url=os.environ.get("MODEL_ENDPOINT"), api_key=os.environ.get("API_KEY"))
        self.sys_msg: list[ChatCompletionSystemMessageParam] = [
            {"role": "system", "content": "Your Name is MyLlama"},
            # {"role": "system", "content": "Do not call tools"},
            # {"role": "system", "content": "You can call tools, however only call them as needed. When a tool returns data, use it as ground truth."},
            # {"role": "system", "content": "Answer the user as naturally as possible."}
        ]
        self.messages: list[ChatCompletionMessageParam] = []

        self.messages.extend(self.sys_msg)
        
        self.model_args = ModelArguments(
            model="qwen3:14b",
            stream=False,
            tools=Tool_Schema.tools,
            tool_choice="auto",
        ).model_dump(exclude_none=True)

    async def chat(self, prompt: str) -> str:

        self.messages.append({"role": "user", "content": prompt})

        response: ChatCompletion = await self.OllamaClient.chat.completions.create(**self.model_args, messages=self.messages)
        # response: ChatCompletion = await self.OllamaClient.chat.completions.create(
        #     model="llama3.2:3b",
        #     stream=False,
        #     messages=self.messages
        # )
        print(response.choices[0].message.content)
        if not response.choices[0].message.tool_calls:
            self.messages.clear()
            self.messages.extend(self.sys_msg)
            return string_utils.cut_reasoning(cast(str, response.choices[0].message.content))
        
        tool_call_result = await self.call_tool(response)

        return tool_call_result
    
    def parse_args(self, json_args: str):

        adapter = TypeAdapter(dict[str, object])
        
        parsed_args = adapter.validate_json(json_args)

        parsed_args.pop('reason')

        print(parsed_args)
        
        return parsed_args

    async def call_tool(self, initial_response: ChatCompletion) -> str:
        
        tool_calls = cast(
            Sequence[ChatCompletionMessageFunctionToolCall],
            initial_response.choices[0].message.tool_calls or [],
        )

        print(initial_response.choices[0].message.tool_calls)
        
        for tool in tool_calls:
            try:
                tool_enum = Tool_Schema.Tool(tool.function.name.strip())

                tool_obj = Tool_Schema.tool_registry[tool_enum.value]
                function_call = tool_obj.fPtr

                args = json.loads(tool.function.arguments or "{}")

                if args:
                    args = self.parse_args(tool.function.arguments)

                if tool_obj.execution == Tool_Schema.Execution.SYNCHRONOUS: 
                    result = function_call(**args)
                
                if tool_obj.execution == Tool_Schema.Execution.ASYNCHRONOUS:
                    result = await function_call(**args)
                    
                if tool_obj.type == Tool_Schema.FunctionType.STATIC:
                    return result
                    
                self.messages.append(cast(ChatCompletionToolMessageParam, {
                    "role": "tool",
                    "tool_call_id": tool.id,
                    "name": tool.function.name,
                    "content": result
                }))

            except ValidationError as e:
                        return "TOOL_CALL ARG ERROR!"
            
            except ValueError:
                return "NOT VALID ENUM - TOOL NOT AVAILABLE!"

        final_response: ChatCompletion = await self.OllamaClient.chat.completions.create(**self.model_args, messages=self.messages)

        return cast(str, final_response.choices[0].message.content)

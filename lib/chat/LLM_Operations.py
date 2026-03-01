import os
from ollama import AsyncClient, ChatResponse
from lib.tools.Tool_Functions import ExternalTools
from lib.tools import Tool_Schema
from typing import AsyncGenerator
import inspect
class LLM_OPS:
    def __init__(self) -> None:
        try:
            self.url = os.environ.get("MODEL_ENDPOINT")
            self.OllamaClient = AsyncClient(host=self.url)
            self.tools = {}
            self.definitions
            self.conversation = []
            print("CONNECTION ESTABLISHED, OLLAMA CLIENT INITIALIZED!")
            
        except:
            print("ERROR INITIALIZING OLLAMA CLIENT!")

    def init_tools(self, external_tools: ExternalTools) -> None:
        for name, method in inspect.getmembers(external_tools, predicate=inspect.ismethod):
            if not name.startswith("_"):
                self.tools[name] = method

    @property
    def definitions(self):
        return [
            method.tool_definition if hasattr(method, "tool_definition") else method
            for method in self.tools.values()
        ]
    
    async def chat(self, prompt: str) -> AsyncGenerator[str, None]:

        self.conversation.append({
            "role": "user",
            "content": prompt
        })

        completed_response = ""

        async for chunk in await self.OllamaClient.chat(
            model="qwen3:14b",
            messages=self.conversation,
            tools=self.definitions,
            think=False,
            stream=True,
        ):
            content = chunk.message.content
            if content:
                completed_response += content
                yield content

        self.conversation.append({
            "role": "assistant",
            "content": completed_response
        })

        print(self.conversation)

    # async def chat(self, prompt: str) -> str | None:

    #     self.conversation.append({
    #         "role": "user",
    #         "content": prompt
    #     })

    #     while True:
    #         response: ChatResponse = await self.OllamaClient.chat(
    #             model="qwen3:14b",
    #             messages=self.conversation,
    #             # tools=[Tool_Functions.time_now],
    #             tools=self.definitions,
    #             think=False,
    #             stream=False,
    #         )

    #         if not response.message.tool_calls:

    #             self.conversation.append({
    #                 "role": "assistant", # change "assistant" to whatever the model name/role is
    #                 "content": response.message.content
    #             })

    #             print(response.message.thinking)

    #             # add sliding window or someother context window management solution - eventually RAG

    #             print(self.conversation)

    #             return response.message.content

    #         self.conversation.append(response.message)

    #         for tool_call in response.message.tool_calls:
    #             tool = self.tools.get(tool_call.function.name)

    #             if tool is None:
    #                 result = f"Unknown tool: {tool_call.function.name}"
    #             else:
    #                 if inspect.iscoroutinefunction(tool):
    #                     result = await tool(**tool_call.function.arguments)
    #                 else:
    #                     result = tool(**tool_call.function.arguments)
                    

    #             self.conversation.append({
    #                 "role": "tool",
    #                 "tool_name": tool_call.function.name,
    #                 "content": result
    #             })

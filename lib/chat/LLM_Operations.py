import os
from ollama import AsyncClient, ChatResponse
from lib.tools.Tool_Functions import ExternalTools
from lib.tools import Tool_Schema
from typing import AsyncGenerator
import inspect
import json
class LLM_OPS:
    def __init__(self) -> None:
        try:
            self.url = os.environ.get("MODEL_ENDPOINT")
            self.OllamaClient = AsyncClient(host=self.url)
            self.tools = {}
            self.definitions
            self.conversation = []
            self.router_instructions = [
                { "role": "system", "content": "You are a router that determines if a user's query requires extra functions to respond." },
                { "role": "system", "content": "Determine if the prompt requires a tool call. Available tools include: smart home management and time tools." },
                { "role": "system", "content": "Determine if the prompt requires the model to think. The model should only think if the user's query is very complex or requires in-depth reasoning" },
                { "role": "system", "content": "Return the requirements in the following format: {tool_call: True/False, think_required: True/False}" },
            ]
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
    
    async def route(self, prompt: str) -> tuple[bool | None, AsyncGenerator[str, None] | str | None]:

        response: ChatResponse = await self.OllamaClient.chat(
            model="qwen3:14b",
            messages=self.router_instructions + [{ "role": "user", "content": prompt }],
            tools=None,
            think=False,
            stream=False
        )

        if not response.message.content:
            print("SOME ERROR OCCURED!")
            return None, None

        router_dict: dict = json.loads(response.message.content)

        print(router_dict)

        tool_call: bool = router_dict.get("tool_call") or False # if tool call is True then stream is False; otherwise stream is always True i.e. tool_call is always False
        think: bool = router_dict.get("think_required") or False

        return (not tool_call, (await self.chat(prompt, think) if tool_call else self.chat_stream(prompt, think)))
    
    async def chat(self, prompt: str, think: bool) -> str | None:

        self.conversation.append({
            "role": "user",
            "content": prompt
        })

        while True:
            response: ChatResponse = await self.OllamaClient.chat(
                model="qwen3:14b",
                messages=self.conversation,
                tools=self.definitions,
                think=think,
                stream=False,
            )

            if not response.message.tool_calls:

                self.conversation.append({
                    "role": "assistant", # change "assistant" to whatever the model name/role is
                    "content": response.message.content
                })

                print(response.message.thinking)

                # add sliding window or someother context window management solution - eventually RAG

                print(self.conversation)

                return response.message.content

            self.conversation.append(response.message)

            for tool_call in response.message.tool_calls:
                tool = self.tools.get(tool_call.function.name)

                if tool is None:
                    result = f"Unknown tool: {tool_call.function.name}"
                else:
                    if inspect.iscoroutinefunction(tool):
                        result = await tool(**tool_call.function.arguments)
                    else:
                        result = tool(**tool_call.function.arguments)
                    

                self.conversation.append({
                    "role": "tool",
                    "tool_name": tool_call.function.name,
                    "content": result
                })

    async def chat_stream(self, prompt: str, think: bool) -> AsyncGenerator[str, None]:

        await self.route(prompt) # this is temporary

        self.conversation.append({
            "role": "user", "content": prompt
        })

        completed_response = ""

        async for chunk in await self.OllamaClient.chat(
            model="qwen3:14b",
            messages=self.conversation,
            tools=None,
            think=think,
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

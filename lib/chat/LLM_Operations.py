import os
from ollama import AsyncClient, ChatResponse
from lib.tools.Tool_Functions import ExternalTools
from lib.tools import Tool_Schema
import inspect
class LLM_OPS:
    def __init__(self) -> None:
        try:
            self.url = os.environ.get("MODEL_ENDPOINT")
            self.OllamaClient = AsyncClient(host=self.url)
            self.tools = {}
            self.conversation = []
            print("CONNECTION ESTABLISHED, OLLAMA CLIENT INITIALIZED!")
            
        except:
            print("ERROR INITIALIZING OLLAMA CLIENT!")

    def init_tools(self, external_tools: ExternalTools) -> None:
        for name, method in inspect.getmembers(external_tools, predicate=inspect.ismethod):
            if not name.startswith("_"):
                self.tools[name] = method

    async def chat(self, prompt: str) -> str | None:

        self.conversation.append({
            "role": "user",
            "content": prompt
        })

        while True:
            response: ChatResponse = await self.OllamaClient.chat(
                model="qwen3:14b",
                messages=self.conversation,
                # tools=[Tool_Functions.time_now],
                tools=list(self.tools.values()),
                stream=False,
                think=False
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
                
                # if tool is None:
                #     result = f"Unknown tool: {tool_call.function.name}"
                # else:
                #     result = await tool.execute(**tool_call.function.arguments)

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

                # if tool and tool.direct_return: // this breaks dynamic tool loading
                #     return result

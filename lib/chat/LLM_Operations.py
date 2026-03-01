import os
from ollama import AsyncClient, ChatResponse
from lib.tools import Tool_Schema, Tool_Functions

class LLM_OPS:
    def __init__(self) -> None:
        try:
            self.OllamaClient: AsyncClient = AsyncClient(host=os.environ.get("MODEL_ENDPOINT"))
            print("CONNECTION ESTABLISHED, OLLAMA CLIENT INITIALIZED!")
            self.conversation = []
        except:
            print("ERROR INITIALIZING OLLAMA CLIENT!")

    async def chat(self, prompt: str) -> str | None:

        self.conversation.append({
            "role": "user",
            "content": prompt
        })

        while True:
            response: ChatResponse = await self.OllamaClient.chat(
                model="qwen3:14b",
                messages=self.conversation,
                tools=[Tool_Functions.time_now],
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
                tool = Tool_Schema.ToolRegistry.get(tool_call.function.name)
                
                if tool is None:
                    result = f"Unknown tool: {tool_call.function.name}"
                else:
                    result = await tool.execute(**tool_call.function.arguments)

                self.conversation.append({
                    "role": "tool",
                    "tool_name": tool_call.function.name,
                    "content": result
                })

                if tool and tool.direct_return:
                    return result

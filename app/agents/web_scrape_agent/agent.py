from langchain_ollama import ChatOllama
from pydantic import BaseModel

from ..base import Agent
from .tools import web_search
from .prompts import SYSTEM_PROMPT


class Reference(BaseModel):
    reference_name: str
    reference_url: str
    reference_title: str
    site_name: str


class WebScrapeResponse(BaseModel):
    keywords: list[str]


class WebScrapeAgent(Agent):

    def __init__(self, llm, tools: list) -> None:
        super().__init__(llm, tools)

    async def invoke(self, input_params):
        graph = self.build()
        return await graph.ainvoke(input_params)


llm = ChatOllama(
    model="qwen3:1.7b",  # or mistral, qwen3, devstral, etc.
    base_url="http://localhost:11434",
    temperature=0,
)
graph = WebScrapeAgent(llm=llm, tools=[]).build(WebScrapeResponse)

inputs = {
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Redis"},
    ]
}


def log_result(result: dict):
    for msg in result.get("messages", []):
        kind = type(msg).__name__

        if kind == "SystemMessage":
            print(f"\n[SYSTEM]\n{msg.content}")

        elif kind == "HumanMessage":
            print(f"\n[USER]\n{msg.content}")

        elif kind == "AIMessage":
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"\n[TOOL CALL] {tc['name']}\n  args: {tc['args']}")
            elif msg.content:
                print(f"\n[ASSISTANT]\n{msg.content}")

        elif kind == "ToolMessage":
            print(f"\n[TOOL RESULT] (call_id={msg.tool_call_id})\n{msg.content}")

        else:
            print(f"\n[{kind.upper()}]\n{msg}")

    structured = result.get("structured_response")
    if structured:
        print(f"\n[STRUCTURED OUTPUT]\n{structured.model_dump_json(indent=2)}")


log_result(graph.invoke(inputs))

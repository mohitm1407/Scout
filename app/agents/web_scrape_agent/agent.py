from langchain_ollama import ChatOllama
from pydantic import BaseModel
import json
import asyncio

from ..base import Agent
from .tools import web_search
from .prompts import SYSTEM_PROMPT


class Reference(BaseModel):
    reference_url: str
    reference_title: str
    reference_description: str


class WebScrapeResponse(BaseModel):
    keywords: list[str]


class WebScrapeAgent(Agent):

    def __init__(self, llm, tools: list) -> None:
        super().__init__(llm, tools)
        self.response = None

    async def invokee(self, user_search_query: str):
        graph = self.build(WebScrapeResponse)
        inputs = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_search_query},
            ]
        }
        results = await graph.ainvoke(inputs)
        sr = results.get("structured_response")
        # self.validate(sr)
        print(type(sr))
        self.response = sr

    def post_process(self) -> list[Reference]:
        references: list[Reference] = []
        for keyword in self.response.keywords:
            search_responses_text = web_search(keyword)
            search_responses = json.loads(search_responses_text)
            for res in search_responses.get("organic"):
                reference = Reference(
                    reference_title=res.get("title"),
                    reference_url=res.get("link"),
                    reference_description=res.get("snippet"),
                )
                references.append(reference)

        return references


llm = ChatOllama(
    model="qwen3:1.7b",  # or mistral, qwen3, devstral, etc.
    base_url="http://localhost:11434",
    temperature=0,
)
graph = WebScrapeAgent(llm=llm, tools=[])

# inputs = {
#     "messages": [
#         {"role": "system", "content": SYSTEM_PROMPT},
#         {"role": "user", "content": "Redis"},
#     ]
# }


# def log_result(result: dict):
#     for msg in result.get("messages", []):
#         kind = type(msg).__name__

#         if kind == "SystemMessage":
#             print(f"\n[SYSTEM]\n{msg.content}")

#         elif kind == "HumanMessage":
#             print(f"\n[USER]\n{msg.content}")

#         elif kind == "AIMessage":
#             if msg.tool_calls:
#                 for tc in msg.tool_calls:
#                     print(f"\n[TOOL CALL] {tc['name']}\n  args: {tc['args']}")
#             elif msg.content:
#                 print(f"\n[ASSISTANT]\n{msg.content}")

#         elif kind == "ToolMessage":
#             print(f"\n[TOOL RESULT] (call_id={msg.tool_call_id})\n{msg.content}")

#         else:
#             print(f"\n[{kind.upper()}]\n{msg}")

#     structured = result.get("structured_response")
#     if structured:
#         print(f"\n[STRUCTURED OUTPUT]\n{structured.model_dump_json(indent=2)}")


async def main():
    response = await graph.invokee("How is Redis better than postgres")
    references = graph.post_process()
    print(type(response))
    print(len(references))


if __name__ == "__main__":
    asyncio.run(main())

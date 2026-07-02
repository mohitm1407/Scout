from langchain_ollama import ChatOllama
from pydantic import BaseModel
import json
import asyncio

from ..base import Agent, Reference
from .tools import web_search
from .prompts import SYSTEM_PROMPT


class WebScrapeResponse(BaseModel):
    keywords: list[str]


class WebScrapeAgent(Agent):

    def __init__(self, llm, tools: list) -> None:
        super().__init__(llm, tools)

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
        self.llm_response = sr
        return sr

    def post_process(self) -> list[Reference]:
        references: list[Reference] = []
        links = []
        for keyword in self.llm_response.keywords:
            search_responses_text = web_search(keyword)
            search_responses = json.loads(search_responses_text)
            if search_responses.get("organic") is None:
                print(keyword + "Is None")
                continue
            for res in search_responses.get("organic"):
                reference = Reference(
                    reference_title=res.get("title"),
                    reference_url=res.get("link"),
                    reference_description=res.get("snippet"),
                )
                if reference.reference_url not in links:
                    references.append(reference)
                    links.append(reference.reference_url)

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
    from ..telemetry_test import get_trace

    tracer = get_trace()

    with tracer.start_as_current_span("web_scrape"):
        user_query = "How is Redis better than postgres"
        response = await graph.invokee(
            user_query,
        )
        references = graph.post_process()
        print(response)
        print(len(references))

    with tracer.start_as_current_span("ranking_agent"):
        from ..ranking_agent.agent import RankingAgent

        ranker = RankingAgent(llm, [], references)
        ranked_results = await ranker.invoke(user_query)
        print(len(ranked_results))
        for res in ranked_results:
            print(
                res.reference_title,
                res.reference_url,
            )

    with tracer.start_as_current_span("extraction_agent"):
        from ..extraction_agent import ExtractionAgent, extract_content, ExtractionOutput

        extractor = ExtractionAgent(llm, [extract_content])
        import asyncio

        async def extract_result(result) -> ExtractionOutput:
            try:
                res = await extractor.invokee(
                    result,
                    user_query,
                )
                return res
            except Exception as e:
                print(f"Error processing result: {e}")
                return None

        tasks = [extract_result(result) for result in ranked_results]

        results = await asyncio.gather(*tasks)
        summaies = []
        print(len(results))
        for res in results:
            if res:
                summaies.append(res.content_summary)


if __name__ == "__main__":
    asyncio.run(main())

from ..base import Agent, Reference
from .tools import rank


class RankingAgent(Agent):
    def __init__(self, llm, tools, references):
        super().__init__(llm, tools)
        self.references: list[Reference] = references

    async def invoke(self, user_query):
        ranked_documents = await rank(self.references, user_query, n=10)
        return ranked_documents

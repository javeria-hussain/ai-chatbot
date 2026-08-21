from app.rag.retriever import RagRetriever
from app.llm.groq_provider import GroqProvider
from app.llm.prompts import SYSTEM_PROMPT
from sqlalchemy.ext.asyncio import AsyncSession

class ChatOrchestrator:
    def __init__(self):
        self.retriever = RagRetriever()
        self.llm = GroqProvider()

    async def get_response(
        self,
        db: AsyncSession,
        user_message: str,
        chat_history: list[dict] | None = None,
    ) -> dict:
        # Step A: Relevant chunks retrieve karo (Day 3 wala kaam)
        results = await self.retriever.retrieve(session=db, query=user_message)
        context = self.retriever.build_context(results)

        # Step B: Agar kuch bhi relevant nahi mila -> fallback
        if not context.strip():
            return {
                "answer": (
                    "I don't have specific information about that yet. "
                    "Would you like me to connect you with our team?"
                ),
                "sources_used": 0,
                "grounded": False,
            }

        # Step C: System prompt mein context bhar do
        system_message = {
            "role": "system",
            "content": SYSTEM_PROMPT.format(context=context),
        }

        # Step D: Conversation history + naya message jodo
        messages = [system_message]
        if chat_history:
            messages.extend(chat_history)
        messages.append({"role": "user", "content": user_message})

        # Step E: Groq se final answer generate karo
        answer = await self.llm.generate(messages)

        return {
            "answer": answer,
            "sources_used": len(results),
            "grounded": True,
        }

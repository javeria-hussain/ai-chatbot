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
        lead_already_captured: bool = False,
    ) -> dict:
        # Step A: Retrive relvent chunks
        results = await self.retriever.retrieve(session=db, query=user_message)
        context = self.retriever.build_context(results)

        # Step B: Nothing relevent found -> fallback
        if not context.strip():
            return {
                "answer": (
                    "I don't have specific information about that yet. "
                    "Would you like me to connect you with our team?"
                ),
                "sources_used": 0,
                "grounded": False,
            }

        # Step C: fill context in system form
        extra_instruction = ""
        if lead_already_captured:
            extra_instruction = (
                "\n\nIMPORTANT: This visitor's contact details (name, email, phone) "
                "have already been collected. Do NOT ask for their name, email, or "
                "phone number again — just answer their question normally."
            )

        system_message = {
            "role": "system",
            "content": SYSTEM_PROMPT.format(context=context) + extra_instruction,
        }

        # Step D: Conversation history + new msg
        messages = [system_message]
        if chat_history:
            messages.extend(chat_history)
        messages.append({"role": "user", "content": user_message})

        # Step E: generate final answer from groq
        answer = await self.llm.generate(messages)

        return {
            "answer": answer,
            "sources_used": len(results),
            "grounded": True,
        }

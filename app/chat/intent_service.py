PRICING_KEYWORDS = [
    "price", "pricing", "cost", "quote", "quotation",
    "how much", "budget", "rates", "charges",
]

BUYING_INTENT_KEYWORDS = [
    "hire", "build me", "i want to build", "develop for us",
    "start a project", "get started", "work with you",
    "need a developer", "custom chatbot", "custom app",
    "automate my business",
]

SERVICE_KEYWORDS = [
    "services", "what do you offer", "capabilities",
    "technologies", "do you build", "can you build", "do you offer",
]


def detect_intent(message: str) -> str:
    text = message.lower()

    if any(keyword in text for keyword in PRICING_KEYWORDS):
        return "pricing_quote"
    if any(keyword in text for keyword in BUYING_INTENT_KEYWORDS):
        return "buying_intent"
    if any(keyword in text for keyword in SERVICE_KEYWORDS):
        return "service_inquiry"
    return "general_query"
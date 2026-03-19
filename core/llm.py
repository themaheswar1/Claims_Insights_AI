import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = "llama-3.3-70b-versatile"

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file.")

def get_chat_llm(temperature: float = 0.3) -> ChatGroq:
    return ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=temperature,
        max_tokens=2048,
    )

def complete(
    system_prompt: str,
    user_message:  str,
    temperature:   float = 0.3,
    max_tokens:    int   = 1024,
) -> str:
    llm = get_chat_llm(temperature=temperature)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]
    response = llm.invoke(messages)
    return response.content.strip()

if __name__ == "__main__":
    print("=" * 45)
    print("  ClaimSight — LLM Connection Test")
    print("=" * 45)

    print("\n[1/2] Testing simple completion...")
    response = complete(
        system_prompt = "You are a helpful assistant. Reply in one sentence only.",
        user_message  = "What is an insurance claim?",
        temperature   = 0.0,
    )
    print(f"  ✅ Response: {response}")

    print("\n[2/2] Testing LangChain ChatGroq...")
    llm    = get_chat_llm(temperature=0.0)
    result = llm.invoke("What is claim settlement in one sentence?")
    print(f"  ✅ Response: {result.content}")

    print("\n✅ LLM connections working.")
    print("=" * 45)
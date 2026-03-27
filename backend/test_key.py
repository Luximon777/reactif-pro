import os
import asyncio
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
key = os.environ.get("EMERGENT_LLM_KEY", "")
print("Key loaded: " + key[:12] + "..." + key[-4:] + " (len=" + str(len(key)) + ")")
from emergentintegrations.llm.chat import LlmChat, UserMessage
chat = LlmChat(api_key=key, session_id="deploy-test", system_message="Say OK").with_model("openai", "gpt-5.2")
result = asyncio.run(chat.send_message(UserMessage(text="Say OK")))
print("LLM TEST OK: " + result[:30])

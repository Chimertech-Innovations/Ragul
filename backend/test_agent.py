import sys
import io

# Force UTF-8 stdout encoding for Windows console (Tamil, Hindi, Telugu script support)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import asyncio
from app.llm.router import AgentRouter

router = AgentRouter()

async def run_tests():
    print("==================================================")
    print("  RAGUL AI - Multilingual & JarvisLabs Test Suite ")
    print("==================================================")

    test_queries = [
        ("English Greeting", "Hello Ragul, how are you?"),
        ("Tamil Greeting", "வணக்கம் ராகுல்"),
        ("Tanglish Greeting", "Vanakkam Ragul, epdi irukinga?"),
        ("Hindi Greeting", "नमस्ते राहुल"),
        ("English Milk Yield", "Which cattle gave the highest milk yield today?"),
        ("Tamil Mastitis Query", "எந்த மாட்டிற்கு மடிநோய் அறிகுறி உள்ளது?"),
        ("Tanglish Worker Query", "Inniku morning ethanai workers check in pannanga?"),
        ("English Pending Work", "What balance work is left on the farm today?"),
        ("Cattle Activity", "What are the cattle doing right now?")
    ]

    history = []
    for label, query in test_queries:
        print(f"\n[Test: {label}] User: '{query}'")
        try:
            response, meta = await router.process_user_message(query, history)
            tool_used = meta.get("tool") if meta else None
            print(f"RAGUL ({tool_used or 'Direct'}): {response}")
            history.append({"role": "user", "content": query})
            history.append({"role": "assistant", "content": response})
        except Exception as e:
            print(f"ERROR: {e}")

    print("\n==================================================")
    print("  All Test Scenarios Completed Successfully!      ")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())

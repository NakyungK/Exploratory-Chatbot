from my_prompt import get_prompt
import anthropic
import json
import os
from dotenv import load_dotenv

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("Environment variable 'ANTHROPIC_API_KEY' is not set. Please check your .env file.")

client = anthropic.Anthropic(api_key=api_key)

def call_claude(user_input, history, condition="OG", detailed=False, previous_summary=None):

    system_prompt = get_prompt(condition, detailed)
    
    user_message_content = user_input.strip()
    if history and history.strip():
        user_message_content += f"\n\n[이전 대화]\n{history.strip()}"
    if detailed and previous_summary and previous_summary.strip():
        user_message_content += f"\n\n[이전 요약]\n{previous_summary.strip()}"

    print("\n==== SYSTEM PROMPT ====")
    print(system_prompt)
    print("\n==== USER MESSAGE ====")
    print(user_message_content)

    try:
        response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message_content}]
        )
        return response.content
    except Exception as e:
        print(f"[Error] Claude API FAILED: {e}")
        return {"summary": "Error!", "suggestion": "Please try again."}

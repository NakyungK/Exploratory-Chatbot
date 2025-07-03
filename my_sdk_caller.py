from my_prompt import get_prompt
import anthropic
import json

client = anthropic.Anthropic()

def call_claude(user_input, history, condition="OG", detailed=False, previous_summary=None):
    """
    Anthropic Claude에 system에는 지침/출력규칙만, 
    messages의 content에만 user input/히스토리/이전요약을 합쳐서 전송하는 함수
    """
    # 1. system 프롬프트는 치환 없이 원본 템플릿만 사용
    system_prompt = get_prompt(condition, detailed)
    
    # 2. user message content를 합성
    user_message_content = user_input.strip()
    if history and history.strip():
        user_message_content += f"\n\n[이전 대화]\n{history.strip()}"
    if detailed and previous_summary and previous_summary.strip():
        user_message_content += f"\n\n[이전 요약]\n{previous_summary.strip()}"

    print("\n==== SYSTEM 프롬프트(지침/구조 ONLY!) ====")
    print(system_prompt)
    print("\n==== USER 질문+대화+요약(실제 메시지) ====")
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
        print(f"[Error] Claude API 호출 실패: {e}")
        return {"summary": "에러가 발생했습니다.", "suggestion": "다시 시도해 주세요."}

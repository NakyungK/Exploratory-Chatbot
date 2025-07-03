import gradio as gr
import json
from my_sdk_caller import call_claude
import pandas as pd
import time
from datetime import datetime

activity_logs = []

def get_prompt_for_log(condition, detailed):
    return f"{condition}{'_detailed' if detailed else ''}"

def extract_before_suggestion(text):
    if "💡" in text:
        return text.split("💡")[0].strip()
    else:
        return text.strip()

def log_activity(user_input, ai_response, prompt, detailed, tab, history, elapsed_time):
    main_response = extract_before_suggestion(ai_response)
    activity_logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tab": tab,
        "user_input": user_input,
        "user_input_length": len(user_input),
        "user_input_tokens": len(user_input.split()),
        "ai_response": ai_response,
        "ai_response_length": len(ai_response),
        "ai_response_tokens": len(ai_response.split()),
        "ai_response_main_length": len(main_response),
        "prompt": prompt,
        "detailed": detailed,
        "history": history,  
        "elapsed_time_sec": elapsed_time
    })

def download_logs():
    if not activity_logs:
        df = pd.DataFrame([{"No logs": ""}])
    else:
        df = pd.DataFrame(activity_logs)
    filename = "activity_logs.xlsx"
    df.to_excel(filename, index=False)
    return filename

custom_css = """
.gradio-container { width: 1400px !important; margin: auto; }

.main-column {
    width: 700px !important;
    max-width: 700px !important;
    min-width: 700px !important;
}

.detail-column { min-width: 500px !important; float: right !important;}

.chatbox { min-height: 500px; }

button.send-btn { background-color: #0056A7 !important; color: white !important; }
button.more-btn { background-color: #B2B2B2 !important; color: black !important; }

#main-column {
    width: 700px !important;
    max-width: 700px !important;
}

.message.bot,
.message-wrap[data-testid="bot"] {
    font-size: 12pt !important;
    word-break: break-word !important;
    overflow-wrap: break-word !important;
    white-space: normal !important;
}

.detail-column,
div[class*="detail-column"] {
    border-left: 2px solid #555 !important;
    padding-left: 15px !important;
    margin-left: 10px !important;
}

.detail-column .markdown-body {
    font-size: 12pt !important;
}

#download_btn {
    font-size: 12px !important;
    padding: 6px 12px !important;
    height: 32px !important;
    width: 100px !important;
    background-color: #474747 !important;
    color: white !important;
}

#download_output {
    font-size: 12px !important;
    padding: 6px 12px !important;
    height: 80px !important;
}
"""

chat_conditions = ["OG", "OS", "PG", "PS"]

def make_history_text(history):
    history_text = ""
    for msg in history:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user":
            history_text += f"User: {content}\n"
        elif role == "assistant":
            history_text += f"AI: {content}\n"
    return history_text.strip()

def safe_parse_claude_response(ai_response):
    if isinstance(ai_response, list):
        ai_response = ai_response[0]
    if hasattr(ai_response, "text"):
        ai_response = ai_response.text
    if isinstance(ai_response, dict):
        summary = ai_response.get("summary", "")
        suggestion = ai_response.get("suggestion", "")
        return f"{summary}\n\n💡 {suggestion}".strip() if suggestion else summary
    try:
        ai_response = str(ai_response)
        parsed = json.loads(ai_response)
        summary = parsed.get("summary", "")
        suggestion = parsed.get("suggestion", "")
        return f"{summary}\n\n💡 {suggestion}".strip() if suggestion else summary
    except Exception:
        import re
        # 더보기 전용: summary만 있는 경우 처리
        summary_only_match = re.search(r'{\s*"summary"\s*:\s*"([^"]+)"\s*}', ai_response)
        if summary_only_match:
            return summary_only_match.group(1)
        
        # 일반 응답: summary + suggestion 처리    
        full_match = re.search(r'"summary"\s*:\s*"([^"]+)",?\s*"suggestion"\s*:\s*"([^"]+)"', ai_response)
        if full_match:
            return f"{full_match.group(1)}\n\n💡 {full_match.group(2)}"
        
        # JSON 형태 제거 후 텍스트만 추출
        cleaned = re.sub(r'^\s*{\s*"summary"\s*:\s*"', '', ai_response)
        cleaned = re.sub(r'"\s*}\s*$', '', cleaned)
        return cleaned.strip().replace('\n', '\n\n')
    
def chatbot_interface(user_input, condition, history):
    start_time = time.time()

    history_text = make_history_text(history)
    prompt = get_prompt_for_log(condition, detailed=False)

    ai_response = call_claude(
        user_input=user_input,
        history=history_text,
        condition=condition,
        detailed=False,
        previous_summary=None
    )
    ai_message = safe_parse_claude_response(ai_response)

    updated_history = history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": ai_message},
    ]
    elapsed = round(time.time() - start_time, 3)
    prompt = get_prompt_for_log(condition, detailed=False)
    log_activity(user_input, ai_message, prompt, detailed=False,
                 tab=condition, history=make_history_text(history), elapsed_time=elapsed)
    return updated_history, "", "", updated_history


def respond_detailed(condition, user_input, history):
    start_time = time.time()

    if not history:
        return history, user_input, "대화 내역이 없습니다. 먼저 질문을 입력한 후 '더보기'를 클릭하세요."

    previous_summary = None
    for msg in reversed(history):
        if msg.get("role") == "assistant":
            content = msg.get("content", "")
            try:
                parsed = json.loads(content)
                previous_summary = parsed.get("summary", content)
            except Exception:
                if "\n\n💡" in content:
                    previous_summary = content.split("\n\n💡")[0].strip()
                else:
                    previous_summary = content.strip()
            break

    if not previous_summary:
        return history, user_input, "이전 대화 요약을 찾을 수 없습니다. 먼저 질문을 입력해 주세요."

    history_text = make_history_text(history)
    ai_response = call_claude(
        user_input=user_input or "",
        history=history_text,
        condition=condition,
        detailed=True,
        previous_summary=previous_summary
    )
    ai_message = safe_parse_claude_response(ai_response)
    detail_str = f"**🔍 자세한 설명:**\n{ai_message}"
    elapsed = round(time.time() - start_time, 3)
    prompt = get_prompt_for_log(condition, detailed=True)
    log_activity(user_input, ai_message, prompt, detailed=True,
                 tab=condition, history=make_history_text(history), elapsed_time=elapsed)
    return history, user_input, detail_str

def reset_app():
    return [], "", ""

with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("### Exploratory Chatbot🧐 (OG / OS / PG / PS)")

    for cond in chat_conditions:
        with gr.Tab(label=cond):
            chat_history_state = gr.State([])

            if cond in ["PG", "PS"]:
                with gr.Row():
                    with gr.Column(scale=3, min_width=600, elem_classes="main-column"):
                        chatbot = gr.Chatbot(label="대화 기록", type="messages")
                        more_btn = gr.Button("더보기", elem_classes="more-btn")
                        user_input = gr.Textbox(label="질문 입력", placeholder="무엇이든 물어보세요!", lines=2)
                        with gr.Row():
                            submit_btn = gr.Button("전송", elem_classes="send-btn")
                            reset_btn = gr.Button("초기화", scale=1)
                        suggestion_output = gr.Markdown(label="💡 프롬프트 제안")

                    with gr.Column(scale=2, min_width=400, elem_classes="detail-column"):
                        detail_output = gr.Markdown(label="🔍 더 자세한 설명", sanitize_html=False)

                submit_btn.click(
                    fn=chatbot_interface,
                    inputs=[user_input, gr.State(cond), chat_history_state],
                    outputs=[chatbot, user_input, detail_output, chat_history_state]
                )

                more_btn.click(
                    fn=respond_detailed,
                    inputs=[gr.State(cond), user_input, chat_history_state],
                    outputs=[chat_history_state, user_input, detail_output]
                )
                reset_btn.click(
                    fn=reset_app,
                    inputs=[],
                    outputs=[chatbot, user_input, detail_output]
                )
                download_btn = gr.Button("log", elem_id="download_btn")
                download_output = gr.File(elem_id="download_output")
                download_btn.click(
                fn=download_logs,
                inputs=[],
                outputs=download_output
                )   

            else:
                with gr.Column(min_width=600, elem_classes="main-column"):
                    chatbot = gr.Chatbot(label="대화 기록", type="messages")
                    user_input = gr.Textbox(label="질문 입력", placeholder="무엇이든 물어보세요!", lines=2)
                    with gr.Row():
                        submit_btn = gr.Button("전송", elem_classes="send-btn")
                        reset_btn = gr.Button("초기화")
                    suggestion_output = gr.Markdown(label="💡 프롬프트 제안")
                    detail_output = gr.Markdown(visible=False, sanitize_html=False)

                submit_btn.click(
                    fn=chatbot_interface,
                    inputs=[user_input, gr.State(cond), chat_history_state],
                    outputs=[chatbot, user_input, detail_output, chat_history_state]
                )
                user_input.submit(
                    fn=chatbot_interface,
                    inputs=[user_input, gr.State(cond), chat_history_state],
                    outputs=[chatbot, user_input, detail_output, chat_history_state]
                )
                reset_btn.click(
                    fn=reset_app,
                    inputs=[],
                    outputs=[chatbot, user_input, detail_output]
                )
                download_btn = gr.Button("log", elem_id="download_btn")
                download_output = gr.File(elem_id="download_output")
                download_btn.click(
                fn=download_logs,
                inputs=[],
                outputs=download_output
                )   


if __name__ == "__main__":
    demo.launch(share=True)

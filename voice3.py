import streamlit as st
import requests
import re
import time
from openai import OpenAI

# ✅ Streamlit 설정
st.set_page_config(page_title="음성으로 질문", page_icon="🎙️", layout="wide")
st.title("🎙️ 음성질문 + 최신정보 + 계산")
st.markdown("#### 🎤 음성으로 질문을 하고, 최신 정보를 검색하여 GPT가 대답합니다.")
st.markdown("- 계산식도 인식 가능 (예: '23 곱하기 4')\n- '그만'이라고 말하면 종료됩니다.")

# ✅ 환경변수에서 키 로드 (Streamlit Cloud의 Advanced Settings > Secrets)
api_key = st.secrets["OPENAI_API_KEY"]
serp_api_key = st.secrets["SERPAPI_API_KEY"]

client = OpenAI(api_key=api_key)

# ✅ 버튼
start_button = st.button("🧠 텍스트 질문 시작", key="start_question")

# 🔍 검색 함수
def search_latest_info(query):
    params = {
        "q": query,
        "api_key": serp_api_key,
        "engine": "google",
        "hl": "ko",
        "gl": "kr"
    }
    response = requests.get("https://serpapi.com/search", params=params)
    if response.status_code == 200:
        data = response.json()
        snippets = [r["snippet"] for r in data.get("organic_results", []) if "snippet" in r]
        return "\n".join(snippets[:3]) if snippets else "관련 정보를 찾을 수 없습니다."
    return "검색 결과를 가져올 수 없습니다."

# ✂️ GPT 요약
def summarize_question(question):
    summary_prompt = f"다음 문장을 간결하게 요약해 주세요 (핵심만 유지, 1문장):\n\n{question}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": summary_prompt}]
    )
    return response.choices[0].message.content.strip()

# ➗ 계산식 판별
def is_math_expression(text):
    pattern = r"^[\d\s\+\-\*/\(\)]+$"
    return re.match(pattern, text.replace(" ", "")) is not None

def evaluate_expression(expr):
    try:
        result = eval(expr)
        return f"{expr} = {result}"
    except Exception:
        return "계산할 수 없습니다."

# ✅ 텍스트 입력 기반 인터랙션 (Streamlit Cloud에서 마이크 미지원 대체)
if start_button:
    user_input = st.text_input("✍️ 질문을 텍스트로 입력해 주세요:", placeholder="예: 오늘 서울 날씨 어때?")

    if user_input:
        expr = user_input.replace(" ", "").replace("x", "*").replace("X", "*")
        if is_math_expression(expr):
            result = evaluate_expression(expr)
            st.write("🧮 계산 결과:", result)
        else:
            with st.spinner("🧠 질문 요약 중..."):
                summarized_question = summarize_question(user_input)
                st.write(f"✂️ 요약된 질문: {summarized_question}")

            with st.spinner("🌐 최신 정보 검색 중..."):
                search_result = search_latest_info(summarized_question)

            with st.spinner("🤖 GPT 응답 생성 중..."):
                prompt = (
                    f"사용자의 질문은 다음과 같습니다: \"{user_input}\"\n"
                    f"질문을 요약하면 다음과 같습니다: \"{summarized_question}\"\n"
                    f"아래는 관련 최신 검색 결과입니다:\n{search_result}\n\n"
                    f"최신 정보를 바탕으로 정확하고 간단하게 한국어로 답변해 주세요."
                )
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = response.choices[0].message.content.strip()
                st.write("🤖 GPT 응답:", answer)

if st.button("🏠 홈으로"):
    st.switch_page("main.py")

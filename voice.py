import streamlit as st
import openai
import os

# OpenAI API 키 설정 (secrets.toml에서 자동 로딩됨)
openai.api_key = os.getenv("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))

# 앱 제목
st.title("🗣️ AI 음성 응답 챗봇")

# 사용자 입력
user_input = st.text_input("질문을 입력해주세요:")

# 입력이 있을 경우 처리
if user_input:
    with st.spinner("답변 생성 중..."):
        try:
            # ChatGPT 응답 생성
            chat_response = openai.chat.completions.create(
                model="gpt-4o",  # 또는 gpt-3.5-turbo
                messages=[
                    {"role": "system", "content": "당신은 친절한 한국어 안내 챗봇입니다."},
                    {"role": "user", "content": user_input}
                ]
            )

            reply = chat_response.choices[0].message.content.strip()
            st.markdown("### 💬 답변")
            st.write(reply)

            # 음성 생성 (OpenAI TTS)
            speech_response = openai.audio.speech.create(
                model="tts-1",
                voice="nova",  # alloy, echo, fable, onyx, nova, shimmer 중 선택
                input=reply
            )

            # mp3 저장 및 재생
            audio_file_path = "output.mp3"
            with open(audio_file_path, "wb") as f:
                f.write(speech_response.content)

            st.audio(audio_file_path, format="audio/mp3")

        except Exception as e:
            st.error(f"오류 발생: {e}")

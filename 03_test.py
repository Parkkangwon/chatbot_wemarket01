import streamlit as st
import openai
import requests
from io import BytesIO

st.title("🖼️ AI 이미지 생성기")
st.write("텍스트와 옵션을 입력하면 다양한 스타일과 크기의 이미지를 생성합니다.")

# 사이드바
st.sidebar.title("🔑 설정")
openai_api_key = st.sidebar.text_input("OpenAI API 키 입력", type="password")

if not openai_api_key:
    st.sidebar.warning("⚠️ OpenAI API 키를 입력하세요.")
    st.stop()

openai.api_key = openai_api_key

# 사용자 입력
prompt = st.text_input("📝 이미지 설명을 입력하세요", value="A cute dog")

style = st.selectbox("🎨 이미지 스타일 선택", [
    "기본", "디지털 아트", "연필 스케치", "3D 렌더링"
])

size_option = st.radio("📐 이미지 크기 선택", [
    "256x256", "512x512", "1024x1024"
], index=2)

# 스타일 추가 프롬프트 설정
style_prompt_map = {
    "기본": "",
    "디지털 아트": ", digital art style",
    "연필 스케치": ", pencil sketch",
    "3D 렌더링": ", 3D render"
}

final_prompt = prompt + style_prompt_map[style]

# 이미지 생성 버튼
if st.button("🖼️ 이미지 2장 생성하기"):
    with st.spinner("이미지를 생성 중입니다..."):
        try:
            for i in range(2):  # 두 번 호출 (각각 n=1)
                response = openai.images.generate(
                    model="dall-e-3",
                    prompt=final_prompt,
                    n=1,
                    size=size_option
                )

                image_url = response.data[0].url
                st.image(image_url, caption=f"{i+1}번 이미지", use_column_width=True)

                # 다운로드 버튼
                img_bytes = requests.get(image_url).content
                st.download_button(
                    label=f"📥 {i+1}번 이미지 다운로드",
                    data=BytesIO(img_bytes),
                    file_name=f"image_{i+1}.png",
                    mime="image/png"
                )

        except Exception as e:
            st.error(f"❌ 이미지 생성 중 오류가 발생했습니다:\n\n{e}")

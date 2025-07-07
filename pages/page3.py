import streamlit as st

st.set_page_config(
    page_title="페이지 3",
    page_icon="⚙️",
)

st.title("페이지 3")
st.write("이것은 세 번째 페이지입니다.")

# 예시 내용
st.header("설정")
theme = st.selectbox("테마 선택", ["Light", "Dark", "Auto"])
language = st.selectbox("언어 선택", ["한국어", "English", "日本語"])

if st.button("설정 저장"):
    st.success("설정이 저장되었습니다!")
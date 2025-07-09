import streamlit as st
import pandas as pd
from datetime import datetime
import time
# from pages import Knowledge_1Generator, Knowledge_2Embedding,User_Question


# 페이지 설정
st.set_page_config(
    page_title="RAG 시스템",
    page_icon="🧠",
    layout="wide",
    # initial_sidebar_state="expanded"
    
)
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    .css-1d391kg {
        display: none !important;
    }
    .css-1rs6os {
        display: none !important;
    }
    .css-17ziqus {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)



# 사이드바 네비게이션
# st.sidebar.title("🧠 RAG 시스템")
# st.sidebar.markdown("---")

# 페이지 선택
page = st.sidebar.selectbox(
    "페이지 선택",
    ["메인 페이지", "Page 1: 지식정보 생성", "Page 2: 지식정보 임베딩", "Page 3: 질문 및 검색"],index=0
)

# 사이드바 정보
# st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 시스템 상태")
# st.sidebar.info("✅ 시스템 정상 작동 중")
st.sidebar.markdown(f"**현재 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")





# 메인 페이지
if page == "메인 페이지":
    # 헤더
    st.title("🧠 지식 정보 관리 시스템")
    # st.markdown("### 효율적인 지식 정보 생성, 임베딩, 검색을 위한 통합 플랫폼")
    
    # 메인 컨테이너
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">
            <h2>📝 Page 1</h2>
            <h3>지식정보 생성</h3>
            <p>새로운 지식 정보를 생성하고 관리합니다</p>
        </div>
        """, unsafe_allow_html=True)
        
        # if st.button("Page 1으로 이동", key="page1_btn", use_container_width=True):
        #     st.session_state.page = "Page 1: 지식정보 생성"
        #     st.rerun()
        if st.button("Page 1으로 이동", key="page1_btn", use_container_width=True):
            st.session_state.page = "Page 1: 지식정보 생성"
            st.switch_page("pages/Knowledge_1Generator.py")
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">
            <h2>🔧 Page 2</h2>
            <h3>지식정보 임베딩</h3>
            <p>생성된 지식 정보를 벡터로 임베딩합니다</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Page 2로 이동", key="page2_btn", use_container_width=True):
            st.session_state.page = "Page 2: 지식정보 임베딩"
            st.switch_page("pages/Knowledge_2Embedding.py")
    
    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">
            <h2>🔍 Page 3</h2>
            <h3>질문 및 검색</h3>
            <p>인덱스를 통해 지식 정보를 검색합니다</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Page 3으로 이동", key="page3_btn", use_container_width=True):
            st.session_state.page = "Page 3: 질문 및 검색"
            st.switch_page("pages/User_Question.py")

elif page == "Page 1: 지식정보 생성":
    st.switch_page("pages/Knowledge_1Generator.py")
elif page == "Page 2: 지식정보 임베딩":
    st.switch_page("pages/Knowledge_2Embedding.py")
elif page == "Page 3: 질문 및 검색" :
    st.switch_page("pages/User_Question.py")
    # 워크플로우 설명
    # st.markdown("---")
    # st.markdown("## 📋 시스템 워크플로우")
    
    # flow_col1, flow_col2, flow_col3 = st.columns(3)
    
    # with flow_col1:
    #     st.markdown("""
    #     **1단계: 지식정보 생성**
    #     - 텍스트 문서 업로드
    #     - 수동 정보 입력
    #     - 데이터 전처리
    #     - 품질 검증
    #     """)
    
    # with flow_col2:
    #     st.markdown("""
    #     **2단계: 지식정보 임베딩**
    #     - 벡터 임베딩 생성
    #     - 차원 축소 (선택사항)
    #     - 임베딩 품질 검증
    #     - 벡터 데이터베이스 저장
    #     """)
    
    # with flow_col3:
    #     st.markdown("""
    #     **3단계: 질문 및 검색**
    #     - 인덱스 설정
    #     - 자연어 질의 처리
    #     - 유사도 검색
    #     - 답변 생성
    #     """)
    
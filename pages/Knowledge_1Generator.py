import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os
from openai import AzureOpenAI
import re

from dotenv import load_dotenv

load_dotenv()

llm_api_key = os.getenv("LLM_API_KEY")
llm_endpoint = os.getenv("LLM_ENDPOINT")
llm_api_version = os.getenv("LLM_API_VERSION")
llm_deployment_name = os.getenv("LLM_DEPLOYMENT_NAME")

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


page = "Page 1: 지식정보 생성"
st.set_page_config(
    page_title="지식정보 생성",
    page_icon="🗄️",
    layout="wide"
)

# 사이드바 설정
page = st.sidebar.selectbox(
    "페이지 선택",
    ["메인 페이지", "Page 1: 지식정보 생성", "Page 2: 지식정보 저장", "Page 3: 질문 및 검색"],index=1
    )
st.sidebar.markdown("### 📊 시스템 상태")
# st.sidebar.info("✅ 시스템 정상 작동 중")
st.sidebar.markdown(f"**현재 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 메인 페이지
if page == "메인 페이지":
    # 헤더
    # st.title("🧠 지식 정보 관리 시스템")
    # st.markdown("### 효율적인 지식 정보 생성, 임베딩, 검색을 위한 통합 플랫폼")
    st.switch_page("./main.py")

elif page == "Page 1: 지식정보 생성":
    # st.switch_page("pages/Knowledge_1Generator.py")
    st.title("🗄️ 지식정보 생성")
elif page == "Page 2: 지식정보 저장":
    st.switch_page("pages/Knowledge_2Embedding.py")
elif page == "Page 3: 질문 및 검색" :
    st.switch_page("pages/User_Question.py")





# 메인 타이틀

st.markdown("---")

# 스키마 입력 방법 선택
input_method = st.radio("스키마 입력 방법을 선택하세요:", ["SQL DDL 입력", "텍스트 입력", "파일 업로드" ])

schema_data = None

if input_method == "텍스트 입력":
    st.subheader("📝 테이블 스키마 정보 입력")
    schema_input = st.text_area(
        "스키마 정보를 입력하세요:",
        height=300,
        help="테이블명, 컬럼명, 데이터 타입, 제약조건 등을 입력하세요",
        placeholder="""예시:
테이블: users
- id: INT PRIMARY KEY AUTO_INCREMENT
- name: VARCHAR(100) NOT NULL
- email: VARCHAR(255) UNIQUE
- created_at: DATETIME DEFAULT CURRENT_TIMESTAMP

테이블: orders
- id: INT PRIMARY KEY AUTO_INCREMENT
- user_id: INT FOREIGN KEY REFERENCES users(id)
- product_name: VARCHAR(200)
- quantity: INT
- price: DECIMAL(10,2)
- order_date: DATETIME"""
    )
    if schema_input:
        schema_data = schema_input

elif input_method == "파일 업로드":
    st.subheader("📁 파일 업로드")
    uploaded_file = st.file_uploader("업로드 파일을 선택하세요", type=['json','txt','md'])
    
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        try:
            if file_extension == 'txt' or 'md':
                schema_data = uploaded_file.read().decode('utf-8')
            elif file_extension == 'json':
                schema_data = json.load(uploaded_file)
        
            
            st.success(f"{file_extension} 파일이 성공적으로 업로드되었습니다!")
            # st.json(schema_data)
        except Exception as e:
            st.error(f"{file_extension} 파일 로드 중 오류 발생: {str(e)}")

elif input_method == "SQL DDL 입력":
    st.subheader("🗃️ SQL DDL 입력")
    ddl_input = st.text_area(
        "DDL 문을 입력하세요:",
        height=300,
        help="CREATE TABLE 문을 입력하세요",
        placeholder="""예시:
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    product_name VARCHAR(200),
    quantity INT,
    price DECIMAL(10,2),
    order_date DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);"""
    )
    if ddl_input:
        schema_data = ddl_input

# 지식정보 생성 옵션
st.subheader("⚙️ 지식정보 생성 옵션")
col1, col2 = st.columns(2)

with col1:
    # knowledge_type = st.selectbox(
    #     "지식정보 유형:",
    #     ["종합 문서", "테이블별 문서", "관계형 다이어그램", "FAQ 형식"]
    # )
    
    output_format = st.selectbox(
        "출력 형식:",
        ["Markdown", "JSON", "텍스트"]
    )

with col2:
    include_examples = st.checkbox("예시 쿼리 포함", value=True)
    include_relationships = st.checkbox("테이블 관계 설명 포함", value=True)
    include_constraints = st.checkbox("제약조건 상세 설명 포함", value=True)
    include_indexing = st.checkbox("인덱싱 가이드 포함", value=False)

# 프롬프트 템플릿 정의
#**문서 유형:** {knowledge_type}

def get_prompt_template(options):
    base_prompt = f"""
당신은 데이터베이스 전문가입니다. 주어진 데이터베이스 스키마를 분석하여 RAG(Retrieval-Augmented Generation) 시스템에서 활용할 수 있는 포괄적인 지식정보 문서를 생성해주세요.

**요구사항:**
1. 각 테이블의 목적과 역할을 명확히 설명
2. 컬럼별 데이터 타입과 제약조건 설명
3. 테이블 간 관계 및 외래키 관계 설명
4. 비즈니스 로직과 데이터 흐름 설명
5. 일반적인 쿼리 패턴과 사용 사례 제시

**출력 형식:** {output_format}

"""
    
    if options.get('include_examples', False):
        base_prompt += "\n6. 각 테이블에 대한 예시 쿼리(SELECT, INSERT, UPDATE, DELETE) 포함"
    
    if options.get('include_relationships', False):
        base_prompt += "\n7. 테이블 간 JOIN 관계와 참조 무결성 설명"
    
    if options.get('include_constraints', False):
        base_prompt += "\n8. 제약조건(PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK 등)의 비즈니스 의미 설명"
    
    if options.get('include_indexing', False):
        base_prompt += "\n9. 성능 최적화를 위한 인덱스 전략 제안"
    
    base_prompt += "\n\n**데이터베이스 스키마:**\n{schema}"
    
    return base_prompt

# Azure OpenAI 클라이언트 초기화
def initialize_azure_client():
    if not all([llm_endpoint, llm_api_key, llm_deployment_name]):
        return None
    
    try:
        client = AzureOpenAI(
            azure_endpoint=llm_endpoint,
            api_key=llm_api_key,
            api_version=llm_api_version
        )
        return client
    except Exception as e:
        st.error(f"Azure OpenAI 클라이언트 초기화 실패: {str(e)}")
        return None

# 지식정보 생성 함수
def generate_knowledge(client, schema_data, options):
    try:
        prompt_template = get_prompt_template(options)
        
        # 스키마 데이터를 문자열로 변환
        if isinstance(schema_data, dict):
            schema_str = json.dumps(schema_data, indent=2, ensure_ascii=False)
        else:
            schema_str = str(schema_data)
        
        prompt = prompt_template.format(schema=schema_str)
        
        response = client.chat.completions.create(
            model=llm_deployment_name,
            messages=[
                {"role": "system", "content": "당신은 데이터베이스 전문가이며, 명확하고 구조화된 문서를 작성하는 것을 전문으로 합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"지식정보 생성 중 오류 발생: {str(e)}")
        return None

# 지식정보 생성 버튼
if st.button("🚀 지식정보 생성", type="primary"):
    if not schema_data:
        st.error("스키마 정보를 입력해주세요!")
    elif not all([llm_endpoint, llm_api_key, llm_deployment_name]):
        
        st.error("Azure OpenAI 설정을 완료해주세요!")
    else:
        # st.write(llm_deployment_name)
        with st.spinner("지식정보를 생성하고 있습니다..."):
            client = initialize_azure_client()
            if client:
                options = {
                    'include_examples': include_examples,
                    'include_relationships': include_relationships,
                    'include_constraints': include_constraints,
                    'include_indexing': include_indexing
                }
                
                knowledge = generate_knowledge(client, schema_data, options)
                
                if knowledge:
                    st.success("지식정보가 성공적으로 생성되었습니다!")
                    
                    # 결과 표시
                    st.subheader("📄 생성된 지식정보")
                    
                    if output_format == "Markdown":
                        st.markdown(knowledge)
                    elif output_format == "JSON":
                        try:
                            json_knowledge = json.loads(knowledge)
                            st.json(json_knowledge)
                        except:
                            st.code(knowledge, language="json")
                    else:
                        st.text(knowledge)
                    
                    # 파일 다운로드 기능
                    st.subheader("💾 파일 다운로드")
                    
                    # 파일명 생성
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_extension = "md" if output_format == "Markdown" else "json" if output_format == "JSON" else "txt"
                    filename = f"db_knowledge_{timestamp}.{file_extension}"
                    
                    # 다운로드 버튼
                    st.download_button(
                        label=f"📥 {filename} 다운로드",
                        data=knowledge,
                        file_name=filename,
                        mime="text/plain" if output_format == "텍스트" else "application/json" if output_format == "JSON" else "text/markdown"
                    )
                    
                    # 미리보기 통계
                    st.subheader("📊 문서 통계")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("총 문자 수", len(knowledge))
                    
                    with col2:
                        st.metric("총 단어 수", len(knowledge.split()))
                    
                    with col3:
                        st.metric("총 줄 수", len(knowledge.split('\n')))

# 사용법 가이드
with st.expander("📚 사용법 가이드"):
    st.markdown("""
    ### 📝 스키마 입력 방법
    - **텍스트 입력**: 자유 형식으로 테이블 구조 입력
    - **JSON 파일**: 구조화된 JSON 형식의 스키마 업로드
    - **SQL DDL**: CREATE TABLE 문 직접 입력
    
    ### 💡 활용 팁
    - 상세한 스키마 정보를 제공할수록 더 정확한 지식정보가 생성됩니다
    - 비즈니스 도메인 정보를 함께 제공하면 더 유용한 문서가 생성됩니다
    - 생성된 문서는 RAG 시스템의 벡터 DB에 저장하여 활용할 수 있습니다
    """)

# 푸터
st.markdown("---")
st.markdown("🔧 **DB Schema to RAG Knowledge Generator** | Made with Streamlit & Azure OpenAI")




    # ### 🎯 지식정보 유형
    # - **종합 문서**: 모든 테이블을 포함한 통합 문서
    # - **테이블별 문서**: 각 테이블별로 별도 섹션
    # - **관계형 다이어그램**: 테이블 간 관계 중심 설명
    # - **FAQ 형식**: 질문-답변 형식의 문서
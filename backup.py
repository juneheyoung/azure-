import streamlit as st
import os
from langchain_openai import AzureOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
#from langchain.callbacks import StreamlitCallbackHandler
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain.schema import Document
import json
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential




load_dotenv()

llm_api_key = os.getenv("LLM_API_KEY")    
llm_endpoint = os.getenv("LLM_ENDPOINT")  
llm_api_version = os.getenv("LLM_API_VERSION")  
llm_deployment_name = os.getenv("LLM_DEPLOYMENT_NAME")

llm_deployment = os.getenv("LLM_DEPLOYMENT_NAME")

embedding_deployment = os.getenv("EMBEDDING_DEPLOYMENT")
embedding_endpoint = os.getenv("EMBEDDING_ENDPOINT")
embedding_api_key = os.getenv("EMBEDDING_API_KEY")
search_endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_AI_SERACH_KEY")
index_name = "langchain-vector-demo"


#azure_embedding_deployment = os.getenv("EMBEDDING_DEPLOYMENT")

# 클라이언트 초기화
search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(search_key)
)

# Streamlit 페이지 설정
st.set_page_config(
    page_title="RAG 시스템 - Azure AI Search",
    page_icon="🔍",
    layout="wide"
)
st.title("🔍 RAG 시스템 - Azure AI Search")
st.markdown("Azure AI Search에 저장된 지식을 활용한 질의응답 시스템")



# 검색 및 답변 설정 (메뉴바 제거 / 인덱스 설정하는 부분 추가 )
with st.sidebar.expander("🎯 검색 및 답변 설정"):
    k = st.slider("검색할 문서 수", min_value=1, max_value=20, value=5)
    search_type = st.selectbox("검색 유형", ["similarity", "mmr", "similarity_score_threshold"])
    
    if search_type == "similarity_score_threshold":
        score_threshold = st.slider("유사도 임계값", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    
    temperature = st.slider("답변 창의성", min_value=0.0, max_value=1.0, value=0.3, step=0.1)
    max_tokens = st.slider("최대 토큰 수", min_value=100, max_value=2000, value=1000, step=100)

# 초기화 함수
@st.cache_resource
def initialize_rag_system(llm_api_key,llm_endpoint,llm_api_version,llm_deployment,embedding_deployment,search_endpoint,search_key,
                          index_name,embedding_endpoint,embedding_api_key):
    """RAG 시스템 초기화"""
    try:
        # Azure OpenAI 임베딩 모델 초기화
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment=embedding_deployment,
            #openai_api_version=llm_api_version,
            azure_endpoint=embedding_endpoint,
            api_key=embedding_api_key
        )
        
        # Azure AI Search 벡터 스토어 초기화
        vector_store = AzureSearch(
            azure_search_endpoint=search_endpoint,
            azure_search_key=search_key,
            index_name=index_name,
            embedding_function=embeddings,
        )
        
        # Azure OpenAI LLM 초기화
        llm = AzureOpenAI(
            deployment_name=llm_deployment,
            # model_name = 'gpt-4.1',
            api_version=llm_api_version,
            azure_endpoint=llm_endpoint,
            api_key=llm_api_key,
            #temperature=temperature,
            #max_tokens=max_tokens
        )
        
        return vector_store, llm, embeddings
        
    except Exception as e:
        st.error(f"RAG 시스템 초기화 중 오류 발생: {str(e)}")
        return None, None, None

# 프롬프트 템플릿
def get_prompt_template():
    template = """
    다음 컨텍스트를 바탕으로 질문에 답하세요. 컨텍스트에 답이 없으면 "제공된 정보로는 답변할 수 없습니다"라고 말하세요.

    컨텍스트:
    {context}

    질문: {question}

    답변을 작성할 때 다음 지침을 따르세요:
    1. 컨텍스트의 정보를 정확하게 사용하세요
    2. 명확하고 구체적으로 답변하세요
    3. 필요하면 단계별로 설명하세요
    4. 한국어로 답변하세요

    답변:
    """
    return PromptTemplate(template=template, input_variables=["context", "question"])




# 메인 애플리케이션
def main():
    # 필수 설정 확인
    if not all([llm_endpoint, llm_api_key, search_endpoint, search_key, index_name]):
        st.warning("⚠️ 모든 필수 설정을 입력해주세요.")
        return
    
    # RAG 시스템 초기화
    vector_store, llm, embeddings = initialize_rag_system(llm_api_key,llm_endpoint,llm_api_version,llm_deployment,embedding_deployment,search_endpoint,search_key,
                          index_name,embedding_endpoint,embedding_api_key)
    if vector_store is None or llm is None:
        st.error("RAG 시스템 초기화에 실패했습니다.")
        return
    
    # embeddings = AzureOpenAIEmbeddings(
    #     azure_deployment=azure_embedding_deployment,  # 실제 배포 이름
    #     #openai_api_version="2024-02-01",
    #     azure_endpoint=embedding_endpoint,
    #     api_key=embedding_api_key 
    # )

    # vector_store = AzureSearch(
    #     azure_search_endpoint=search_endpoint,
    #     azure_search_key=search_key,
    #     index_name="langchain-vector-demo",  # 기존 인덱스 이름
    #     embedding_function=embeddings,
    # )

    # llm = AzureOpenAI(
    # azure_endpoint=llm_endpoint,
    # api_key=llm_api_key,
    # api_version=llm_api_version,
    # model = llm_deployment
    # )
    # llm = AzureOpenAI(
    # azure_deployment=llm_deployment,
    # openai_api_version=llm_api_version,
    # azure_endpoint=llm_endpoint,
    # api_key=llm_api_key,
    #temperature=temperature,
    #max_tokens=max_tokens
    # )
   # =    llm_deployment

    # 연결 테스트
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 벡터 스토어 연결 테스트"):
            try:
                # 간단한 검색 테스트
                result = search_client.search("*", include_total_count=True, top=0)
                document_count = result.get_count()

                st.success(f"✅ 벡터 스토어 연결 성공! (인덱스: {index_name})")
                st.info(f"검색된 문서 수: {document_count}")
            except Exception as e:
                st.error(f"❌ 벡터 스토어 연결 실패: {str(e)}")
    
    with col2:
        if st.button("🤖 LLM 연결 테스트"):
            try:
                test_response = llm.invoke("안녕하세요")
                #llm.completions.create(prompt = "안녕하세요")
                st.success("✅ LLM 연결 성공!")
                st.info(f"테스트 응답: {test_response[:100]}...")
            except Exception as e:
                st.error(f"❌ LLM 연결 실패: {str(e)}")
    
    st.divider()
    
    # 질의응답 섹션
    st.header("💬 질의응답")
    
    # 질문 입력
    question = st.text_input("💭 질문을 입력하세요:", placeholder="예: 회사의 주요 제품은 무엇인가요?")
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        search_button = st.button("🔍 검색", type="primary")
    
    with col2:
        if st.button("🗑️ 대화 기록 삭제"):
            if 'chat_history' in st.session_state:
                del st.session_state['chat_history']
            st.rerun()
    
    # 검색 및 답변 생성
    if search_button and question:
        with st.spinner("검색 중..."):
            try:
                # 검색 설정
                search_kwargs = {"k": k}
                if search_type == "similarity_score_threshold":
                    search_kwargs["score_threshold"] = score_threshold
                
                # 벡터 스토어에서 관련 문서 검색
                if search_type == "mmr":
                    retrieved_docs = vector_store.max_marginal_relevance_search(
                        question, k=k
                    )
                elif search_type == "similarity_score_threshold":
                    retrieved_docs = vector_store.similarity_search_with_relevance_scores(
                        question, k=k
                    )
                    # 임계값 필터링
                    retrieved_docs = [doc for doc, score in retrieved_docs if score >= score_threshold]
                else:
                    retrieved_docs = vector_store.similarity_search(question, k=k)
                
                # 검색 결과 표시
                st.subheader("📚 검색된 관련 문서")
                
                if retrieved_docs:
                    for i, doc in enumerate(retrieved_docs[:3]):  # 최대 3개만 표시
                        with st.expander(f"문서 {i+1} (출처: {doc.metadata.get('source', 'Unknown')})"):
                            st.write(doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content)
                            st.json(doc.metadata)
                    
                    # 컨텍스트 생성
                    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
                    
                    # 프롬프트 생성
                    prompt_template = get_prompt_template()
                    prompt = prompt_template.format(context=context, question=question)
                    
                    # LLM으로 답변 생성
                    st.subheader("🤖 AI 답변")
                    
                    with st.spinner("답변 생성 중..."):
                        try:
                            response = llm.invoke(prompt)
                            st.write(response)
                            
                            # 대화 기록 저장
                            if 'chat_history' not in st.session_state:
                                st.session_state['chat_history'] = []
                            
                            st.session_state['chat_history'].append({
                                "question": question,
                                "answer": response,
                                "retrieved_docs": len(retrieved_docs),
                                "timestamp": st.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            
                        except Exception as e:
                            st.error(f"답변 생성 중 오류 발생: {str(e)}")
                
                else:
                    st.warning("관련 문서를 찾을 수 없습니다. 검색 설정을 조정해보세요.")
                    
            except Exception as e:
                st.error(f"검색 중 오류 발생: {str(e)}")
    
    # 대화 기록 표시
    if 'chat_history' in st.session_state and st.session_state['chat_history']:
        st.divider()
        st.header("📋 대화 기록")
        
        for i, chat in enumerate(reversed(st.session_state['chat_history'])):
            with st.expander(f"💭 {chat['question'][:50]}... ({chat['timestamp']})"):
                st.write("**질문:**", chat['question'])
                st.write("**답변:**", chat['answer'])
                st.write(f"**검색된 문서 수:** {chat['retrieved_docs']}")

if __name__ == "__main__":
    main()
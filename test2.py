import os
import streamlit as st 
from langchain_openai import AzureOpenAI, AzureOpenAIEmbeddings
# from langchain_community.vectorstores import AzureSearch
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
#from langchain.callbacks import StreamlitCallbackHandler
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain.schema import Document
import json
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from azure.search.documents.indexes import SearchIndexClient
from langchain_community.vectorstores.azuresearch import AzureSearch
from azure.search.documents.models import VectorizableTextQuery

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



st.set_page_config(
    page_title="RAG 시스템 - Azure AI Search",
    page_icon="🔍",
    layout="wide"
)
st.title("🔍 RAG 시스템 - Azure AI Search")
st.markdown("Azure AI Search에 저장된 지식을 활용한 질의응답 시스템")

with st.sidebar.expander("🎯 검색 및 답변 설정"):
    try:
    # SearchIndexClient 생성
        credential = AzureKeyCredential(search_key)
        client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
        indexes = client.list_indexes()
        name_box = []
        if indexes :
            for index in indexes:
                name_box.append(index.name)
        st.subheader("index 설정")
        selected_selectbox = st.selectbox("항목을 선택하세요:", name_box)
        st.write("선택된 항목:", selected_selectbox)
        st.divider()
        index_name = selected_selectbox
    except Exception as e:
        print(f"Error: {e}")

search_client = SearchClient(endpoint=search_endpoint,
                             index_name=index_name,
                             search_type="hybrid",
                             credential=AzureKeyCredential(search_key))


openai_client = AzureOpenAI(
    api_version=llm_api_version,
    azure_endpoint=llm_endpoint,
    api_key=llm_api_key
)

def rag_query(user_question):
    # 1. 벡터 검색으로 관련 문서 찾기
    search_results = search_client.search(
        search_text=user_question,
        top=5,
        select=["content", "metadata"]  # 필요한 필드만 선택
    )
    
    # 2. 검색된 문서들을 컨텍스트로 구성
    context = ""
    for result in search_results:
        context += f"{result['content']}\n\n"

    # 3. 프롬프트 구성
    prompt = f"""
    다음 문서들을 참고하여 질문에 답변해주세요:
    
    문서 내용:
    {context}
    
    질문: {user_question}
    
    답변:
    """
    
    # 4. LLM에게 답변 요청
    response = openai_client.chat.completions.create(
        model=llm_deployment,
        messages=[
            {"role": "system", "content": "당신은 제공된 문서를 기반으로 정확한 답변을 제공하는 AI 어시스턴트입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content

answer = st.text_input("질문을 입력하세요:", placeholder="궁금한 내용을 입력해주세요...")

# 질문이 입력되었을 때만 답변 생성
if answer:
    with st.spinner("답변을 생성하고 있습니다..."):
        try:
            llm_answer = rag_query(answer)
            st.write("### 답변:")
            st.write(llm_answer)
        except Exception as e:
            st.error(f"답변 생성 중 오류가 발생했습니다: {str(e)}")
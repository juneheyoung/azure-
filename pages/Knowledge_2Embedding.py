import os
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
import streamlit as st
import json

import tempfile
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document

from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
import pandas as pd 
from azure.search.documents import SearchClient

load_dotenv()

llm_api_key = os.getenv("LLM_API_KEY")
llm_endpoint = os.getenv("LLM_ENDPOINT")
llm_api_version = os.getenv("LLM_API_VERSION")
llm_deployment_name = os.getenv("LLM_DEPLOYMENT_NAME")
ai_search_endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
ai_search_api_key = os.getenv("AZURE_AI_SERACH_KEY")
azure_embedding_endpoint = os.getenv("EMBEDDING_ENDPOINT")
azure_embedding_api_key = os.getenv("EMBEDDING_API_KEY")
azure_embedding_deployment = os.getenv("EMBEDDING_DEPLOYMENT")

# Option 2: Use AzureOpenAIEmbeddings with an Azure account
embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
    azure_deployment=azure_embedding_deployment,
    #openai_api_version=azure_openai_api_version,
    azure_endpoint=azure_embedding_endpoint,
    api_key=azure_embedding_api_key,
)

# 인덱스 목록 조회
tab1, tab2 = st.tabs(["📋 인덱스 목록", "➕ 새 인덱스 생성"])        
with tab1:
    
    st.header("인덱스 목록")
            
    try:
        # SearchIndexClient 생성
        credential = AzureKeyCredential(ai_search_api_key)
        client = SearchIndexClient(endpoint=ai_search_endpoint, credential=credential)
        #indexes = list(client.list_indexes())
        indexes = client.list_indexes()
        name_box = []
        if indexes :
            for index in indexes:
                name_box.append(index.name)
        
            
            st.subheader("index 설정")
            selected_selectbox = st.selectbox("항목을 선택하세요:", name_box)
            st.write("선택된 항목:", selected_selectbox)
            st.divider()
            new_index_name = selected_selectbox
        
            if new_index_name != None :
                vector_store: AzureSearch = AzureSearch(
                azure_search_endpoint=ai_search_endpoint,
                azure_search_key=ai_search_api_key,
                index_name=new_index_name,
                embedding_function=embeddings.embed_query,
                )
                search_client = SearchClient(
                    endpoint=ai_search_endpoint,
                    index_name=new_index_name,
                    credential=AzureKeyCredential(ai_search_api_key)
                )

                st.subheader("📁 TXT 파일 업로드")
                uploaded_file = st.file_uploader("TXT 파일을 선택하세요", type=['txt'])

                if uploaded_file is not None:
                    try:
                        # 파일 내용 직접 읽기
                        content = uploaded_file.read().decode('utf-8')
                        
                        # Document 객체 직접 생성
                        document = Document(
                            page_content=content,
                            metadata={"source": uploaded_file.name, "type": "txt"}
                        )
                        st.success("TXT 파일이 성공적으로 로드되었습니다!")
                        st.write(f"파일 크기: {len(content)} 문자")
                        
                        # 텍스트 분할
                        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                        docs = text_splitter.split_documents([document])
                        
                        result = search_client.search("*", include_total_count=True, top=0)
                        document_count = result.get_count()
                        
                        st.success(f"총 {len(docs)}개의 문서 청크가 추가되었습니다!")
                        st.info(f"검색된 문서 수: {document_count}")
                        # 벡터 스토어에 저장
                        vector_store.add_documents(documents=docs)
                        st.success("문서가 벡터 스토어에 저장되었습니다!")
                        
                    except Exception as e:
                        st.error(f"TXT 파일 처리 중 오류 발생: {str(e)}")
                    
    except Exception as e:
        print(f"Error: {e}")

with tab2:

    st.header("새 인덱스 생성")
    
    with st.form("new_index_form"):
        st.subheader("기본 정보")
        
        # 인덱스 이름
        new_index_name = st.text_input(
            "인덱스 이름 *",
            placeholder="예: my-search-index",
            help="?영문 소문자, 숫자, 하이픈만 사용 가능"
        ) 
        submitted = st.form_submit_button("인덱스 생성", type="primary")       
        if submitted and new_index_name:
            vector_store: AzureSearch = AzureSearch(
            azure_search_endpoint=ai_search_endpoint,
            azure_search_key=ai_search_api_key,
            index_name=new_index_name,
            embedding_function=embeddings.embed_query,
            )

            st.subheader("📁 TXT 파일 업로드")
            uploaded_file = st.file_uploader("TXT 파일을 선택하세요", type=['txt'])

            if uploaded_file is not None:
                try:
                    # 파일 내용 직접 읽기
                    content = uploaded_file.read().decode('utf-8')
                    
                    # Document 객체 직접 생성
                    document = Document(
                        page_content=content,
                        metadata={"source": uploaded_file.name, "type": "txt"}
                    )
                    st.success("TXT 파일이 성공적으로 로드되었습니다!")
                    st.write(f"파일 크기: {len(content)} 문자")
                    
                    # 텍스트 분할
                    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                    docs = text_splitter.split_documents([document])
                    
                    st.success(f"총 {len(docs)}개의 문서 청크가 생성(추가)되었습니다!")
                    
                    # 벡터 스토어에 저장
                    vector_store.add_documents(documents=docs)
                    st.success("문서가 벡터 스토어에 저장되었습니다!")
                    
                except Exception as e:
                    st.error(f"TXT 파일 처리 중 오류 발생: {str(e)}")








### index 삭제 
### input data - type  지정하기 
### 문서갯수 원래거 포함해서 총개수로 나오게 하기 

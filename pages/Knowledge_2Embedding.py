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

load_dotenv()

azure_openai_api_key = os.getenv("OPEN_API_KEY")
azure_endpoint = os.getenv("AZURE_ENDPOINT")
azure_openai_api_version = os.getenv("API_VERSION")
azure_deployment = os.getenv("DEPLOYMENT_NAME")

vector_store_address = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
vector_store_password = os.getenv("AZURE_AI_SERACH_KEY")

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

index_name: str = "langchain-vector-demo"   ### index_name change ? 
vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=vector_store_address,
    azure_search_key=vector_store_password,
    index_name=index_name,
    embedding_function=embeddings.embed_query,
)

### json 추가 / 다른것 추가 /// 

# file upload 하기 

# schema_data = None

# st.subheader("📁 TXT 파일 업로드")
# uploaded_file = st.file_uploader("TXT 파일을 선택하세요", type=['txt'])
# if uploaded_file is not None:
#     try:
#         schema_data = TextLoader(uploaded_file, encoding='utf-8')
#         st.success("TXT 파일이 성공적으로 로드되었습니다!")
#         # st.text(schema_data)
#     except Exception as e:
#         st.error(f"TXT 파일 로드 중 오류 발생: {str(e)}")
    

    
#     loader = uploaded_file

#     documents = loader.load()
#     text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
#     docs = text_splitter.split_documents(documents)

#     vector_store.add_documents(documents=docs)

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
        
        st.success(f"총 {len(docs)}개의 문서 청크가 생성되었습니다!")
        
        # 벡터 스토어에 저장
        vector_store.add_documents(documents=docs)
        st.success("문서가 벡터 스토어에 저장되었습니다!")
        
    except Exception as e:
        st.error(f"TXT 파일 처리 중 오류 발생: {str(e)}")
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


embeddings = AzureOpenAIEmbeddings(
    azure_deployment= embedding_deployment,
    api_version= '1',
    azure_endpoint= embedding_endpoint,
    api_key= embedding_api_key,
)

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


vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint= search_endpoint, # ai search 서비스의 엔드포인트
    azure_search_key=search_key, # ai search 서비스의 키
    index_name=index_name,
    search_type="hybrid", # hybrid 가 기본 값이다.
    embedding_function=embeddings.embed_query,
    additional_search_client_options={"retry_total": 3, "api_version":"2024-12-01-preview"},
)






# langchan-openai 라이브러리 필요
# openai 모델
client = AzureOpenAI(
    api_version=llm_api_version,
    azure_endpoint=llm_endpoint,
    api_key=llm_api_key
)
deployment = llm_deployment_name


# AI Search service
search_api_key= search_key
search_endpoint= search_endpoint


index_name = index_name

search_client = SearchClient(endpoint=search_endpoint,
                             index_name=index_name,
                             credential=AzureKeyCredential(search_api_key))


@tool
def search_ktds(query, top_k=3):
    """
    ktds 회사의 비즈니스 정보를 검색합니다.

    Args:
        query (str): 검색할 키워드 또는 질문입니다. 예시: 'ktds의 빅데이터 사업'
        top_k (int, optional): 반환할 결과의 개수입니다. 기본값은 3입니다. 예시: 5

    Returns:
        list: 검색 결과 리스트
    """
    vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=top_k,
                                     fields="metadata")
    results = search_client.search(search_text=query, vector_queries=[vector_query],
                                filter=None, top=top_k)

    return [ doc for doc in results]
    
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage, SystemMessage

class AgentState(MessagesState):
  ...

# pip install langchan-openai
deployment = llm_deployment_name

llm = AzureChatOpenAI(
    azure_deployment=deployment,
    api_version=llm_api_version,
    azure_endpoint=llm_endpoint,
    temperature=0.,
    api_key=llm_api_key
)

agent_engine = llm.bind_tools(tools=[search_ktds])

tool_node = ToolNode([search_ktds])


def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def call_model(state: AgentState):
    sys_prompt = SystemMessage("You are a helpful AI assiatant. When you use tool, you must say based on the tool result.")
    response = agent_engine.invoke([sys_prompt] + state['messages'])
    return {"messages": [response]}

# --------- Define the graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    ["tools", END]
)
workflow.add_edge("tools", "agent")

graph = workflow.compile()


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


question = "ktds 회사의 정보보안 비지니스에 대해서 알려줘"
inputs = {"messages": [("user", question)]}

# print_stream(graph.stream(inputs, stream_mode="values"))
# st.write(graph.stream(inputs, stream_mode="values"))
import streamlit as st

st.set_page_config(
    page_title="페이지 2",
    page_icon="📈",
)

st.title("페이지 2")
st.write("이것은 두 번째 페이지입니다.")

# 예시 내용
st.header("차트 섹션")
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_title("Sine Wave")
st.pyplot(fig)









    # embeddings = AzureOpenAIEmbeddings(
    #     azure_deployment=azure_embedding_deployment,  # 실제 배포 이름
    #     #openai_api_version="2024-02-01",
    #     azure_endpoint=azure_embedding_endpoint,
    #     api_key=azure_embedding_api_key 
    # )

    # vector_store = AzureSearch(
    #     azure_search_endpoint=search_endpoint,
    #     azure_search_key=search_key,
    #     index_name="langchain-vector-demo",  # 기존 인덱스 이름
    #     embedding_function=embeddings,
    # )

    # llm = AzureOpenAI(
    # azure_endpoint=azure_endpoint,
    # api_key=azure_api_key,
    # api_version=api_version,
    # model = llm_deployment
    # )
    # llm = AzureOpenAI(
    # azure_deployment=llm_deployment,
    # openai_api_version=api_version,
    # azure_endpoint=azure_endpoint,
    # api_key=azure_api_key,
    #temperature=temperature,
    #max_tokens=max_tokens
    # )
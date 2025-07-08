import streamlit as st



def print_messages():
    if "messages" in st.session_state and len(st.session_state["messages"]) > 0:
        for role, message in st.session_state["messages"]:
            st.chat_message(role).write(message)

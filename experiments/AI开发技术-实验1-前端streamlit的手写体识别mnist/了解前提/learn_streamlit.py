import streamlit as st
st.title("Hello Streamlit!")
promot = st.chat_input("输入")

if promot:
    user = st.chat_message("user")
    user.write(promot)

    ai = st.chat_message("assistant")
    ai.write("你好")

import json
import logging
import time
import requests

import streamlit as st
from tenacity import retry, stop_after_attempt, wait_exponential


st.title("Chatbot UI")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=20)
)
def get_bot_response(text):
    url = f"http://chatbot-api:8000/chat/complete"

    payload = json.dumps({
        "message": text
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
    if response.status_code != 200:
        raise TimeoutError(f"Request to bot fail: {response.text}")
    return json.loads(response.text)


# Streamed response
def response_generator(user_message):
    res = get_bot_response(user_message)
    for line in res.split("\n\n"):
        logging.info(f"Line: {line}")
        for sen in line.split("\n"):
            yield sen + '\n\n'
            time.sleep(0.05)
        yield '\n'
    return res


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(prompt))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

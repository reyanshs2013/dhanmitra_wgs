import streamlit as st
from huggingface_hub import InferenceClient

st.title("My School Chatbot")

# Safely fetch the token from Streamlit secrets
if "HF_TOKEN" not in st.secrets:
    st.error("Missing 'HF_TOKEN' in secrets! Please add it to secrets.toml or your cloud dashboard.")
    st.stop()

hf_token = st.secrets["HF_TOKEN"]

# Set up the client and model
client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=hf_token
)

# Start chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat_completion(
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    max_tokens=500,
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {e}")

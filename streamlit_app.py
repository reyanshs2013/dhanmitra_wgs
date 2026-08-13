import streamlit as st
from huggingface_hub import InferenceClient

st.title("💰 AI Financial Advisor")
st.caption("A school project chatbot specialized in personal finance, budgeting, and investment basics.")

# Safely fetch the token from Streamlit secrets
if "HF_TOKEN" not in st.secrets:
    st.error("Missing 'HF_TOKEN' in secrets! Please add it to secrets.toml or your cloud dashboard.")
    st.stop()

hf_token = st.secrets["HF_TOKEN"]

# UPDATED: Configured to use Llama 3.1 8B Instruct
client = InferenceClient(
    model="Qwen/Qwen3.8-2.4T-A95B",
    token=hf_token
)

# FIXED SYSTEM PROMPT: Enforces domain authority and boundaries
SYSTEM_PROMPT = (
    "You are an expert personal financial advisor designed for a student school project. "
    "Your job is to answer questions strictly related to personal finance, budgeting, saving, "
    "taxes, investing, and macroeconomics. "
    "CRITICAL RULE: If the user asks any question outside of the financial advisor domain "
    "(such as coding, history, science, sports, creative writing, or general chitchat), "
    "you must politely decline to answer, stating that you only specialize in financial guidance."
)

# Start chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("Ask a financial question (e.g., How do I build a budget?)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing markets..."):
            try:
                # Prepend the system prompt so the model never forgets its rules
                api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                for m in st.session_state.messages:
                    api_messages.append({"role": m["role"], "content": m["content"]})

                response = client.chat.completions.create(
                    messages=api_messages,
                    max_tokens=600,
                    temperature=0.3 # Lower temperature makes the bot more consistent and strict
                )
                
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                # Check for common gating errors
                if "gated" in str(e).lower() or "not found" in str(e).lower():
                    st.error("Error: Please make sure you have accepted Meta's terms on the Hugging Face website for Llama-3.1-8B-Instruct using your account.")
                else:
                    st.error(f"Error: {e}")

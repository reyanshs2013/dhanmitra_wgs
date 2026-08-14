# Dhan Mitra — Station 5: AI Financial Coach

A student-built Streamlit prototype for the Dhan Mitra Station 5 exhibition.

## What it demonstrates

- Hugging Face Inference Providers via `huggingface_hub.InferenceClient`
- Personalised AI financial education using a Dhan Mitra system prompt
- Interactive visitor profile
- Financial Wellness Score (clearly labelled as an educational prototype score)
- Monthly cash-flow bar chart
- Compound-growth comparison bar chart
- Prompt-engineering demonstration: vague vs personalised prompt
- Chat interface using Streamlit's `st.chat_message` and `st.chat_input`
- Student presentation / talking points
- Safety guardrails: no guaranteed returns and no pretending to be a regulated adviser


## Hugging Face

The app uses `huggingface_hub.InferenceClient` and the chat-completions interface.
If the default model is unavailable through your selected Inference Provider, change
`HF_MODEL` in secrets or use the model field in the sidebar.

## Deployment

For Streamlit Community Cloud, add `HF_TOKEN` and optionally `HF_MODEL` in the app's
Secrets settings. Do not commit your real token to GitHub.

## Exhibition flow

1. Enter visitor profile in the sidebar.
2. Show the cash-flow chart and Wellness Score.
3. Demonstrate the compound-growth chart.
4. Show vague vs personalised prompts.
5. Click "Generate the personalised prompt answer".
6. Ask a live question in the chat box.
7. Finish with the 30-second student pitch.

## Important

This is an educational prototype. Financial projections are illustrations based on
assumptions. They are not guarantees of returns or personalised regulated investment advice.

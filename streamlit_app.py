"""Dhanmitra — AI Financial Coach (Station 5)

Deploy on Streamlit Community Cloud. Add this to secrets:
HF_TOKEN = "your_hugging_face_token"

Recommended requirements.txt:
streamlit
pandas
huggingface_hub>=0.28.0
"""

import math
import re
from datetime import datetime

import pandas as pd
import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(
    page_title="Dhanmitra | AI Financial Coach",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Styling ---------------------------------------------------------------
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg,#f6fbff 0%,#eefaf4 60%,#fff9eb 100%);}
    [data-testid="stSidebar"] {background: #082f49;}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stCaption {color: #f8fafc !important;}
    /* Keep expander headers and their open panels dark, so labels stay visible. */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: #0b3b57 !important; border: 1px solid #25627c; border-radius: 10px; overflow: hidden;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] details,
    [data-testid="stSidebar"] [data-testid="stExpander"] summary,
    [data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: #0b3b57 !important; color: #f8fafc !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary * {color: #f8fafc !important;}
    [data-testid="stSidebar"] [data-testid="stExpander"] div[data-baseweb="slider"] * {color: #f8fafc !important;}
    .hero {padding: 1.4rem 1.7rem; border-radius: 22px; background: linear-gradient(120deg,#0f766e,#0284c7); color:white; box-shadow:0 10px 30px rgba(2,132,199,.22); margin-bottom:1rem;}
    .hero h1 {margin:0; font-size:2.1rem;}
    .hero p {margin:.35rem 0 0; font-size:1.05rem; opacity:.95;}
    .metric-card {background:white; border-radius:16px; padding:.8rem 1rem; border:1px solid #dcecf1; box-shadow:0 3px 12px rgba(15,118,110,.08);}
    .badge {display:inline-block; padding:.22rem .7rem; border-radius:99px; background:#d1fae5; color:#065f46; font-size:.82rem; font-weight:700;}
    .disclaimer {background:#fff7ed; border-left:4px solid #f59e0b; padding:.7rem 1rem; border-radius:8px; color:#78350f;}
    .stButton > button {border-radius:12px; border:0; font-weight:650; padding:.5rem .8rem;}
</style>
""", unsafe_allow_html=True)

# ---- Finance calculations --------------------------------------------------
def money(value: float) -> str:
    return f"₹{value:,.0f}"


def months_to_goal(target: float, saved: float, monthly: float) -> int | None:
    remaining = max(target - saved, 0)
    return math.ceil(remaining / monthly) if monthly > 0 else None


def sip_future_value(monthly: float, annual_rate: float, years: int) -> float:
    """Future value of a monthly SIP, with contributions at month-end."""
    n = max(years * 12, 1)
    r = annual_rate / 12 / 100
    return monthly * n if r == 0 else monthly * (((1 + r) ** n - 1) / r)


def investment_profile(risk_score: int) -> tuple[str, str, float]:
    if risk_score <= 4:
        return "Cautious", "Prioritise safety and an emergency fund before taking investment risk.", 6.5
    if risk_score <= 7:
        return "Balanced", "Mix stability with growth; diversify instead of chasing one option.", 10.0
    return "Growth-focused", "You can consider a longer-term growth approach, while understanding volatility.", 12.0


def wellness_score(income: float, needs: float, wants: float, savings: float) -> int:
    if income <= 0:
        return 0
    savings_rate = savings / income
    needs_rate = needs / income
    wants_rate = wants / income
    score = 45 + min(savings_rate * 180, 35) + max(0, (0.60 - needs_rate) * 35) + max(0, (0.25 - wants_rate) * 30)
    return int(max(0, min(100, round(score))))


def finance_only(question: str) -> bool:
    finance_terms = {
        "money", "budget", "save", "saving", "income", "expense", "spend", "spending", "loan", "debt",
        "interest", "invest", "investment", "mutual", "fund", "sip", "stock", "share", "gold", "fd",
        "fixed deposit", "bank", "tax", "insurance", "credit", "wallet", "goal", "wealth", "finance",
        "financial", "wellness", "wellness score", "score", "rupee", "₹", "emergency",
        "compound", "return", "risk", "salary", "cash", "improve my score", "money map",
    }
    normalized = question.lower()
    return any(term in normalized for term in finance_terms)


def get_client() -> InferenceClient | None:
    try:
        token = st.secrets.get("HF_TOKEN")
    except Exception:
        token = None
    # "auto" routes the request to a Hugging Face inference provider that supports the model.
    # Without it, some deployments use a legacy endpoint that rejects chat-completion requests.
    return InferenceClient(provider="groq", api_key=token) if token else None


def ask_coach(question: str, profile: dict) -> str:
    client = get_client()
    if client is None:
        return "I cannot connect to the Hugging Face chat model"

    system_prompt = f"""You are Dhanmitra, an encouraging AI financial-literacy coach for a Class-8 school project in India.
Only answer questions about personal finance, budgeting, saving, goals, investments, risk, interest, banking, insurance, taxes, or financial literacy. For any other topic, politely say: "I’m Dhanmitra, your finance coach. Please ask me a money or financial-literacy question."
Use plain, student-friendly English. Be educational, not promotional. Do not claim to be a licensed adviser, give guaranteed returns, or tell the visitor to buy/sell a specific security. Use words such as "consider", "learn", and "discuss with a trusted adult/qualified professional". Keep the response under 180 words.
Always clarify: SIP is a method of investing regularly; a mutual fund is an investment product.

Visitor snapshot (use only when relevant):
Monthly income: {money(profile['income'])}; monthly needs: {money(profile['needs'])}; monthly wants: {money(profile['wants'])}; monthly savings: {money(profile['savings'])}; wellness score: {profile['wellness']}/100.
Goal: {profile['goal']} worth {money(profile['target'])}; already saved: {money(profile['saved'])}; monthly goal contribution: {money(profile['goal_monthly'])}; estimated time remaining: {profile['goal_months']} months.
Risk profile: {profile['risk_name']} (score {profile['risk_score']}/10). Wealth Lab example: {money(profile['sip_monthly'])}/month for {profile['years']} years at an assumed {profile['return_rate']}% annual return could grow to approximately {money(profile['future_value'])}; this is an illustration, not a promise.
"""

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": question}]
    errors = []
    try:
        # Current Hugging Face chat-completions interface.
        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instant",
            messages=messages,
            max_tokens=300,
            temperature=0.35,
        )
        answer = response.choices[0].message.content
        if answer:
            return answer
    except Exception as exc:
        errors.append(f"{model}: {type(exc).__name__}")

# ---- Session state ---------------------------------------------------------
def init_state() -> None:
    defaults = {"messages": [], "pending_question": None}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

# ---- Sidebar: visitor inputs from Stations 1–4 -----------------------------
st.sidebar.title("🧩 Visitor Snapshot")
st.sidebar.caption("Quick inputs collected from Stations 1–4")

with st.sidebar.expander("1️⃣ Smart Wallet", expanded=True):
    income = st.slider("Monthly income (₹)", 5_000, 200_000, 40_000, 1_000)
    needs = st.slider("Monthly needs (₹)", 0, 150_000, 18_000, 500)
    wants = st.slider("Monthly wants (₹)", 0, 100_000, 7_000, 500)
    savings = st.slider("Monthly savings (₹)", 0, 100_000, 10_000, 500)

with st.sidebar.expander("2️⃣ Goal+ Planner", expanded=True):
    goal = st.selectbox("Main goal", ["New phone", "Higher education", "Family trip", "Emergency fund", "New bicycle", "Other dream"])
    target = st.slider("Goal amount (₹)", 5_000, 500_000, 60_000, 1_000)
    saved = st.slider("Already saved (₹)", 0, 500_000, 15_000, 1_000)
    goal_monthly = st.slider("Monthly contribution (₹)", 500, 50_000, 3_000, 500)

with st.sidebar.expander("3️⃣ Invest Smart", expanded=False):
    risk_score = st.slider("Comfort with investment ups and downs", 1, 10, 5)

with st.sidebar.expander("4️⃣ Wealth Lab", expanded=False):
    sip_monthly = st.slider("Monthly investment illustration (₹)", 500, 25_000, 2_000, 500)
    years = st.slider("Time period (years)", 1, 30, 10)
    return_rate = st.slider("Assumed annual return (%)", 0.0, 18.0, 10.0, 0.5)

wellness = wellness_score(income, needs, wants, savings)
goal_months = months_to_goal(target, saved, goal_monthly)
risk_name, risk_tip, suggested_rate = investment_profile(risk_score)
future_value = sip_future_value(sip_monthly, return_rate, years)
profile = dict(income=income, needs=needs, wants=wants, savings=savings, wellness=wellness,
               goal=goal, target=target, saved=saved, goal_monthly=goal_monthly,
               goal_months=goal_months or 0, risk_score=risk_score, risk_name=risk_name,
               sip_monthly=sip_monthly, years=years, return_rate=return_rate, future_value=future_value)

# ---- Main dashboard --------------------------------------------------------
st.markdown("""
<div class="hero">
  <span class="badge">STATION-5 : The Heart of Dhan Mitra</span>
  <h1>💰 Dhanmitra AI Financial Coach</h1>
  <p>Your friendly guide to smarter money choices — powered by your own Station 1–4 story.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="disclaimer">🎓 <b>Learning tool only:</b> This app explains finance in simple language. It does not give guaranteed returns or personal investment orders.</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Wellness score", f"{wellness}/100", "Budget snapshot")
m2.metric("Goal progress", f"{min(saved / max(target, 1) * 100, 100):.0f}%", f"{money(max(target-saved, 0))} to go")
m3.metric("Risk profile", risk_name, f"{risk_score}/10")
m4.metric("Wealth Lab estimate", money(future_value), f"{years}-year illustration")

left, right = st.columns([1.1, 1])
with left:
    st.subheader("📊 Your money map")
    spending_data = pd.DataFrame({"Category": ["Needs", "Wants", "Savings", "Unallocated"],
                                  "Amount": [needs, wants, savings, max(income-needs-wants-savings, 0)]})
    st.bar_chart(spending_data.set_index("Category"), color="#0f766e", height=260)
    if needs + wants + savings > income:
        st.warning("Your selected spending is higher than income. Ask the coach how to rebalance it.")
    else:
        st.caption("A healthy plan usually leaves room for goals, surprises, and fun.")

with right:
    st.subheader("🎯 Goal+ forecast")
    progress = min(saved / max(target, 1), 1.0)
    st.progress(progress, text=f"{money(saved)} of {money(target)} saved")
    if goal_months is not None:
        finish = pd.Timestamp.today() + pd.DateOffset(months=goal_months)
        st.info(f"At {money(goal_monthly)}/month, your {goal.lower()} goal may take about **{goal_months} months** — around **{finish.strftime('%B %Y')}**.")
    st.caption(f"Risk coach note: {risk_tip}")
    st.caption(f"Illustration rate selected: {return_rate:.1f}% a year. Real returns can be higher or lower.")

st.subheader("🧠 Prompt Engineering Lab")
st.caption("See why a specific question gives Dhanmitra enough context to give a useful answer.")

vague_question = "How can I save money?"
vague_answer = "Track your spending, reduce unnecessary purchases, and try to save regularly."
specific_question = (
    f"My monthly income is {money(income)}. I spend {money(needs)} on needs and "
    f"{money(wants)} on wants. I have saved {money(saved)} towards my {goal.lower()} "
    f"goal of {money(target)}. How can I reach it sooner?"
)
extra_needed = max(target - saved, 0)
personalised_answer = (
    f"You have saved {money(saved)} of your {money(target)} {goal.lower()} goal. "
    f"At {money(goal_monthly)} each month, the remaining {money(extra_needed)} may take about "
    f"{goal_months} months. Start by reviewing the {money(wants)} you spend on wants: moving even "
    f"₹500 per month from wants to this goal could shorten the wait. Keep your savings contribution "
    f"automatic and review the plan each month."
)

vague_col, specific_col = st.columns(2)
with vague_col:
    st.markdown("#### 😶 Vague prompt")
    st.info(vague_question)
    st.caption("**Typical answer:** " + vague_answer)
with specific_col:
    st.markdown("#### ✨ Personalised prompt")
    st.success(specific_question)
    st.caption("**More actionable answer:** " + personalised_answer)
    if st.button("💬 Ask this personalised prompt", use_container_width=True):
        st.session_state.pending_question = specific_question

st.subheader("💬 Ask your AI coach")
st.caption("Try a quick prompt, or use the personalised prompt above. This demonstrates prompt engineering!")
quick_prompts = [
    "How can I improve my wellness score?",
    "Explain compound growth using my Wealth Lab numbers.",
    "Can I reach my goal one month earlier?",
    "What does my risk profile mean?",
    "What is the difference between an SIP and a mutual fund?",
]
cols = st.columns(3)
for index, prompt in enumerate(quick_prompts):
    with cols[index % 3]:
        if st.button(prompt, key=f"quick_{index}", use_container_width=True):
            st.session_state.pending_question = prompt

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask a finance question… e.g., How can I save for my goal faster?")
question = question or st.session_state.pending_question
if question:
    st.session_state.pending_question = None
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        if not finance_only(question):
            answer = "I’m Dhanmitra, your finance coach. Please ask me a money or financial-literacy question. 💰"
            st.markdown(answer)
        else:
            with st.spinner("Dhanmitra is thinking…"):
                answer = ask_coach(question, profile)
            st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

c1, c2 = st.columns([1, 5])
with c1:
    if st.button("🧹 Clear chat"):
        st.session_state.messages = []
        st.rerun()
with c2:
    st.caption("Dhan Mitra helps you understand where your money currently goes BEFORE suggesting where to put it")

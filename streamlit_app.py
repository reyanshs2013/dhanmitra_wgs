import os
import math
import random
import streamlit as st
import pandas as pd
import plotly.express as px
from huggingface_hub import InferenceClient

# ============================================================
# DHAN MITRA
# Complete Streamlit financial-literacy application
# ============================================================

st.set_page_config(
    page_title="Dhan Mitra",
    page_icon="💚",
    layout="wide"
)

# ---------------- CONFIG ----------------

def get_secret(name, default=""):
    try:
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass
    return os.getenv(name, default)

HF_TOKEN = get_secret("HF_TOKEN")
HF_MODEL = get_secret(
    "HF_MODEL",
    "Qwen/Qwen3.8-2.4T-A95B"
)

# ---------------- FINANCE-ONLY AI ----------------

SYSTEM_PROMPT = """
You are Dhan Mitra, an AI financial-literacy coach.

You ONLY answer finance and financial-literacy questions.

Allowed topics:
budgeting, saving, spending, income, expenses, financial goals,
emergency funds, debt, EMI, compound interest, SIP, mutual funds,
fixed deposits, stocks, bonds, gold, inflation, risk, diversification,
retirement, pension, insurance, taxes at a general educational level,
wealth building, portfolio concepts, assets, liabilities and net worth.

If the user asks a non-finance question, respond exactly:
"Sorry, I am Dhan Mitra. I can answer only finance and
financial-literacy questions."

Rules:
- Never guarantee investment returns.
- Do not claim to be a SEBI-registered adviser.
- Do not give personalized buy/sell instructions for individual securities.
- Explain concepts in simple language.
- Clearly label projections as illustrations.
- Explain that SIP is a method and a Mutual Fund is a product.
- If a question is outside finance, do not answer it even if it is harmless.
"""

FINANCE_TERMS = {
    "finance", "financial", "money", "budget", "budgeting", "saving",
    "savings", "save", "spending", "expense", "expenses", "income",
    "invest", "investment", "investing", "investor", "stock", "stocks",
    "share", "shares", "mutual fund", "mutual funds", "sip",
    "systematic investment", "fixed deposit", "fd", "gold", "bond",
    "bonds", "loan", "loans", "debt", "emi", "interest", "compound",
    "compounding", "inflation", "tax", "taxes", "wealth", "portfolio",
    "risk", "diversification", "return", "returns", "goal", "goals",
    "emergency fund", "retirement", "pension", "nps", "insurance",
    "net worth", "cash flow", "asset", "assets", "liability",
    "liabilities", "sip vs mutual fund", "asset allocation"
}

def is_finance_question(question):
    q = question.lower().strip()
    return any(term in q for term in FINANCE_TERMS)

def ask_huggingface(messages):
    if not HF_TOKEN:
        return (
            "⚠️ Hugging Face is not connected. Add HF_TOKEN to "
            "Streamlit Secrets to activate the AI coach."
        )

    try:
        client = InferenceClient(
            api_key=HF_TOKEN,
            provider="auto"
        )

        result = client.chat.completions.create(
            model=HF_MODEL,
            messages=messages,
            max_tokens=700,
            temperature=0.25
        )

        return result.choices[0].message.content

    except Exception as error:
        return f"⚠️ Hugging Face connection error: {error}"

# ---------------- CALCULATIONS ----------------

def calculate_wellness(income, spending, savings, existing_savings, emi):
    if income <= 0:
        return 0

    savings_rate = savings / income
    expense_ratio = spending / income
    debt_ratio = emi / income

    savings_points = min(30, savings_rate / 0.20 * 30)

    if expense_ratio <= .50:
        expense_points = 25
    elif expense_ratio <= .60:
        expense_points = 22
    elif expense_ratio <= .70:
        expense_points = 18
    elif expense_ratio <= .80:
        expense_points = 13
    elif expense_ratio <= .90:
        expense_points = 8
    else:
        expense_points = 3

    if debt_ratio == 0:
        debt_points = 25
    elif debt_ratio <= .10:
        debt_points = 22
    elif debt_ratio <= .20:
        debt_points = 17
    elif debt_ratio <= .30:
        debt_points = 10
    else:
        debt_points = 5

    buffer = existing_savings / income

    if buffer >= 6:
        readiness_points = 20
    elif buffer >= 3:
        readiness_points = 15
    elif buffer >= 1:
        readiness_points = 10
    else:
        readiness_points = 5

    return max(
        0,
        min(
            100,
            round(
                savings_points +
                expense_points +
                debt_points +
                readiness_points
            )
        )
    )

def compound_value(monthly, years, annual_rate):
    r = annual_rate / 12
    n = years * 12

    if r == 0:
        return monthly * n

    return monthly * (((1 + r) ** n - 1) / r) * (1 + r)

# ---------------- SESSION ----------------

if "chat" not in st.session_state:
    st.session_state.chat = []

if "context" not in st.session_state:
    st.session_state.context = {
        "income": 50000,
        "existing_savings": 50000,
        "housing": 10000,
        "food": 6000,
        "transport": 4000,
        "shopping": 5000,
        "emi": 5000,
        "savings": 5000,
        "goal": "Emergency Fund",
        "target": 100000,
        "goal_saved": 20000,
        "risk": "Not assessed"
    }

ctx = st.session_state.context

# ---------------- STYLE ----------------

st.markdown("""
<style>
.stApp {
    background: #f3f8f5;
}
.hero {
    background: linear-gradient(135deg,#063b2b,#087f5b,#19a974);
    color: white;
    padding: 35px;
    border-radius: 28px;
    margin-bottom: 24px;
    box-shadow: 0 12px 32px rgba(0,0,0,.15);
}
.hero h1 {
    font-size: 50px;
    margin: 0;
}
.hero p {
    font-size: 18px;
}
.card {
    background: white;
    border: 1px solid #d8e8df;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 6px 18px rgba(0,0,0,.06);
    min-height: 160px;
}
.ai {
    background: linear-gradient(135deg,#052f24,#087f5b);
    color: white;
    border-radius: 24px;
    padding: 28px;
}
.tip {
    background: #e7f7ee;
    border-left: 6px solid #0a8c63;
    padding: 18px;
    border-radius: 10px;
}
.reject {
    background: #fff0f0;
    border-left: 6px solid #d33d3d;
    padding: 16px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>💚 DHAN MITRA</h1>
    <h2>AI FINANCIAL COACH</h2>
    <p>
    <b>Your financial-literacy companion</b><br>
    Understand → Budget → Save → Set Goals → Learn Risk →
    See Compound Growth → Ask the AI
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------- NAVIGATION ----------------

st.sidebar.title("💚 Dhan Mitra")
page = st.sidebar.radio(
    "Choose a section",
    [
        "🏠 Home",
        "💰 Station 1 — Smart Wallet",
        "🎯 Station 2 — Goal+",
        "📊 Station 3 — Invest Smart",
        "📈 Station 4 — Wealth Lab",
        "🤖 Station 5 — AI Financial Coach",
        "🔄 Flowchart"
    ]
)

st.sidebar.info(
    "🔒 The AI accepts finance and financial-literacy questions only."
)

# ============================================================
# HOME
# ============================================================

if page == "🏠 Home":

    st.markdown("## 💚 The Heart of Dhan Mitra")

    spending = (
        ctx["housing"] +
        ctx["food"] +
        ctx["transport"] +
        ctx["shopping"] +
        ctx["emi"]
    )

    score = calculate_wellness(
        ctx["income"],
        spending,
        ctx["savings"],
        ctx["existing_savings"],
        ctx["emi"]
    )

    a, b, c, d = st.columns(4)
    a.metric("💚 Wellness Score", f"{score}/100")
    b.metric("💰 Income", f"₹{ctx['income']:,.0f}")
    c.metric("📉 Spending", f"₹{spending:,.0f}")
    d.metric("🎯 Goal", ctx["goal"])

    st.markdown("## 🧭 Five-Part Journey")

    stations = [
        ("💰", "Station 1", "Smart Wallet",
         "Understand where your money goes."),
        ("🎯", "Station 2", "Goal+",
         "Save with a purpose."),
        ("📊", "Station 3", "Invest Smart",
         "Understand risk and investment concepts."),
        ("📈", "Station 4", "Wealth Lab",
         "Make compound growth visible."),
        ("🤖", "Station 5", "AI Financial Coach",
         "Ask finance questions and receive financial-literacy answers.")
    ]

    cols = st.columns(5)

    for col, (icon, station, title, description) in zip(cols, stations):
        with col:
            st.markdown(
                f"""
                <div class="card">
                    <div style="font-size:42px">{icon}</div>
                    <small>{station}</small>
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    tips = [
        "Track your spending before deciding how much you can invest.",
        "Give every savings target a clear purpose and deadline.",
        "An emergency fund can help protect your financial plan from surprises.",
        "SIP is a method; a Mutual Fund is a product.",
        "Compound growth becomes more powerful as time increases."
    ]

    st.markdown("## 💡 Dhan Mitra Tip")

    if "tip" not in st.session_state:
        st.session_state.tip = random.choice(tips)

    st.markdown(
        f'<div class="tip"><b>💡 Tip:</b> {st.session_state.tip}</div>',
        unsafe_allow_html=True
    )

    if st.button("🔄 New Finance Tip"):
        st.session_state.tip = random.choice(tips)
        st.rerun()

# ============================================================
# STATION 1
# ============================================================

elif page == "💰 Station 1 — Smart Wallet":

    st.markdown("## 💰 Station 1 — Smart Wallet")
    st.subheader("Do you know where your money goes?")
    st.write(
        "This is the diagnostic stage. Understand cash flow, spending "
        "and savings capacity before making investment decisions."
    )

    income = st.number_input(
        "Monthly income (₹)",
        0, 10000000, ctx["income"], 1000
    )

    existing = st.number_input(
        "Existing savings (₹)",
        0, 100000000, ctx["existing_savings"], 5000
    )

    st.markdown("### Six categories")

    left, right = st.columns(2)

    with left:
        housing = st.number_input(
            "🏠 Housing & Utilities (₹)",
            0, 10000000, ctx["housing"], 500
        )
        food = st.number_input(
            "🍎 Food (₹)",
            0, 10000000, ctx["food"], 500
        )
        transport = st.number_input(
            "🚗 Transport (₹)",
            0, 10000000, ctx["transport"], 500
        )

    with right:
        shopping = st.number_input(
            "🛍️ Shopping & Entertainment (₹)",
            0, 10000000, ctx["shopping"], 500
        )
        emi = st.number_input(
            "💳 Debt / EMIs (₹)",
            0, 10000000, ctx["emi"], 500
        )
        savings = st.number_input(
            "📈 Savings & Investments (₹)",
            0, 10000000, ctx["savings"], 500
        )

    if st.button("🧮 Calculate Wellness Score", type="primary"):

        spending = housing + food + transport + shopping + emi
        surplus = income - spending - savings

        score = calculate_wellness(
            income, spending, savings, existing, emi
        )

        ctx.update({
            "income": income,
            "existing_savings": existing,
            "housing": housing,
            "food": food,
            "transport": transport,
            "shopping": shopping,
            "emi": emi,
            "savings": savings
        })

        x, y, z = st.columns(3)
        x.metric("💚 Financial Wellness", f"{score}/100")
        y.metric("📉 Monthly Spending", f"₹{spending:,.0f}")
        z.metric("💵 Monthly Surplus", f"₹{surplus:,.0f}")

        chart = pd.DataFrame({
            "Category": [
                "Housing", "Food", "Transport",
                "Shopping", "Debt / EMI", "Savings"
            ],
            "Amount": [
                housing, food, transport,
                shopping, emi, savings
            ]
        })

        fig = px.bar(
            chart,
            x="Category",
            y="Amount",
            text="Amount",
            title="Where Your Money Goes"
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# STATION 2
# ============================================================

elif page == "🎯 Station 2 — Goal+":

    st.markdown("## 🎯 Station 2 — Goal+ Planner")
    st.subheader("Don't just save. Save with a purpose.")

    goal = st.text_input("Your financial goal", ctx["goal"])

    target = st.number_input(
        "Target amount (₹)",
        0, 100000000, ctx["target"], 5000
    )

    saved = st.number_input(
        "Already saved (₹)",
        0, 100000000, ctx["goal_saved"], 1000
    )

    monthly = st.number_input(
        "Monthly saving capacity (₹)",
        0, 10000000, 10000, 500
    )

    remaining = max(target - saved, 0)

    months = math.ceil(remaining / monthly) if monthly else None

    progress = min(saved / target, 1) if target else 0

    st.progress(progress)

    st.metric(
        "Estimated time to goal",
        f"{months} months" if months else "Enter a monthly saving amount"
    )

    faster = monthly * 1.15

    if faster > 0:
        faster_months = math.ceil(remaining / faster)

        st.info(
            f"💡 Saving 15% more each month (₹{faster:,.0f}) "
            f"could reduce the simple saving period to about "
            f"**{faster_months} months**."
        )

    ctx.update({
        "goal": goal,
        "target": target,
        "goal_saved": saved
    })

# ============================================================
# STATION 3
# ============================================================

elif page == "📊 Station 3 — Invest Smart":

    st.markdown("## 📊 Station 3 — Invest Smart")
    st.subheader("Which option suits YOU?")

    q1 = st.radio(
        "If your investment temporarily fell 20%, what would you do?",
        [
            "I would be very uncomfortable.",
            "I could tolerate it.",
            "I could accept it for long-term growth."
        ]
    )

    q2 = st.radio(
        "When might you need the money?",
        [
            "1–3 years",
            "3–7 years",
            "More than 7 years"
        ]
    )

    q3 = st.radio(
        "What matters most?",
        [
            "Protecting money",
            "Balance",
            "Long-term growth"
        ]
    )

    risk_points = (
        1 if "very uncomfortable" in q1 else
        2 if "tolerate" in q1 else 3
    )

    risk_points += (
        1 if "1–3" in q2 else
        2 if "3–7" in q2 else 3
    )

    risk_points += (
        1 if "Protecting" in q3 else
        2 if "Balance" in q3 else 3
    )

    profile = (
        "Conservative" if risk_points <= 4 else
        "Moderate" if risk_points <= 7 else
        "Aggressive"
    )

    ctx["risk"] = profile

    st.success(
        f"Educational risk profile: **{profile}**"
    )

    st.info(
        "📚 Financial-literacy distinction: "
        "**SIP is a method of investing. Mutual Fund is a product.** "
        "A person can invest in a Mutual Fund via SIP."
    )

    comparison = pd.DataFrame({
        "Option": [
            "Fixed Deposit", "Gold", "Mutual Funds", "Stocks"
        ],
        "Illustrative Relative Risk": [1, 3, 3, 5]
    })

    fig = px.bar(
        comparison,
        x="Option",
        y="Illustrative Relative Risk",
        text="Illustrative Relative Risk",
        title="Educational Relative Risk Scale"
    )

    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# STATION 4
# ============================================================

elif page == "📈 Station 4 — Wealth Lab":

    st.markdown("## 📈 Station 4 — Wealth Lab")
    st.subheader("Show me the numbers!")

    monthly = st.number_input(
        "Monthly investment (₹)",
        100, 1000000, 500, 100
    )

    years = st.slider(
        "Number of years",
        1, 40, 20
    )

    rate = st.slider(
        "Assumed annual return (%)",
        0.0, 20.0, 12.0, 0.5
    )

    data = []

    for year in range(1, years + 1):

        invested = monthly * year * 12

        projected = compound_value(
            monthly,
            year,
            rate / 100
        )

        data.append({
            "Year": year,
            "Invested": invested,
            "Illustrative Value": projected
        })

    df = pd.DataFrame(data)

    fig = px.bar(
        df,
        x="Year",
        y=["Invested", "Illustrative Value"],
        barmode="group",
        title="Compound Growth Illustration"
    )

    st.plotly_chart(fig, use_container_width=True)

    final_value = compound_value(
        monthly, years, rate / 100
    )

    st.success(
        f"Illustrative value after {years} years: "
        f"**₹{final_value:,.0f}**"
    )

    st.warning(
        "This is a mathematical illustration based on an assumed rate. "
        "Actual investment returns can vary."
    )

# ============================================================
# STATION 5
# ============================================================

elif page == "🤖 Station 5 — AI Financial Coach":

    st.markdown("## 🤖 Station 5 — Dhan Mitra AI")

    st.markdown("""
    <div class="ai">
        <h2>💚 Your Finance-Only AI Coach</h2>
        <p>
        Ask me about budgeting, saving, goals, compound interest,
        SIPs, mutual funds, risk, debt, inflation, retirement,
        investing concepts and other finance topics.
        </p>
        <p><b>🚫 Non-finance questions are automatically rejected.</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # Financial context supplied to the model.
    spending = (
        ctx["housing"] +
        ctx["food"] +
        ctx["transport"] +
        ctx["shopping"] +
        ctx["emi"]
    )

    score = calculate_wellness(
        ctx["income"],
        spending,
        ctx["savings"],
        ctx["existing_savings"],
        ctx["emi"]
    )

    with st.expander("🧠 View information available to the AI"):

        st.json({
            "monthly_income": ctx["income"],
            "monthly_spending": spending,
            "monthly_savings": ctx["savings"],
            "existing_savings": ctx["existing_savings"],
            "financial_wellness_score": score,
            "goal": ctx["goal"],
            "goal_target": ctx["target"],
            "risk_profile": ctx["risk"]
        })

    for message in st.session_state.chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask Dhan Mitra a finance question..."
    )

    if question:

        st.session_state.chat.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        # HARD FINANCE GATE
        if not is_finance_question(question):

            answer = (
                "Sorry, I am Dhan Mitra. "
                "I can answer only finance and financial-literacy questions."
            )

            with st.chat_message("assistant"):
                st.markdown(
                    f'<div class="reject">🚫 {answer}</div>',
                    unsafe_allow_html=True
                )

        else:

            context_message = f"""
Visitor financial context:
Monthly income: ₹{ctx["income"]:,.0f}
Monthly spending: ₹{spending:,.0f}
Monthly savings/investments: ₹{ctx["savings"]:,.0f}
Existing savings: ₹{ctx["existing_savings"]:,.0f}
Financial Wellness Score: {score}/100
Goal: {ctx["goal"]}
Goal target: ₹{ctx["target"]:,.0f}
Educational risk profile: {ctx["risk"]}

Use this context only when useful. Explain that the Wellness
Score is a project metric, not an official financial standard.
"""

            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "system",
                    "content": context_message
                }
            ]

            messages.extend(
                st.session_state.chat[-8:]
            )

            with st.chat_message("assistant"):

                with st.spinner("💚 Dhan Mitra is thinking..."):
                    answer = ask_huggingface(messages)

                st.markdown(answer)

        st.session_state.chat.append({
            "role": "assistant",
            "content": answer
        })

# ============================================================
# FLOWCHART
# ============================================================

elif page == "🔄 Flowchart":

    st.markdown("## 🔄 Dhan Mitra Flowchart")

    st.markdown("""
```text
                         ┌─────────────────┐
                         │   👤 USER       │
                         └────────┬────────┘
                                  │
                                  ▼
                     ┌────────────────────────┐
                     │   💚 DHAN MITRA  │
                     └───────────┬────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
 ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
 │ 💰 STATION 1   │     │ 🎯 STATION 2   │     │ 📊 STATION 3   │
 │ SMART WALLET   │────▶│ GOAL+ PLANNER  │────▶│ INVEST SMART   │
 │                │     │                │     │                │
 │ Income         │     │ Goal           │     │ Risk Questions │
 │ 6 Categories   │     │ Target         │     │ Risk Profile   │
 │ Savings        │     │ Timeline       │     │ SIP vs MF      │
 │ Wellness Score │     └───────┬────────┘     └───────┬────────┘
 └───────┬────────┘             │                      │
         │                      └──────────┬───────────┘
         │                                 │
         └────────────────┬────────────────┘
                          ▼
                 ┌────────────────┐
                 │ 📈 STATION 4   │
                 │ WEALTH LAB     │
                 │                │
                 │ Monthly Amount │
                 │ Years          │
                 │ Return Assump. │
                 │ Compound Growth│
                 └───────┬────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ 🧠 USER CONTEXT  │
                │                  │
                │ Budget           │
                │ Wellness Score   │
                │ Goal             │
                │ Risk Profile     │
                │ Growth Math      │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ 🤖 STATION 5     │
                │ AI FINANCIAL     │
                │ COACH            │
                └────────┬─────────┘
                         │
                         ▼
                 ┌────────────────┐
                 │ FINANCE TOPIC? │
                 └───────┬────────┘
                    YES / \ NO
                       /   \
                      ▼     ▼
          ┌────────────────┐ ┌─────────────────────┐
          │ Hugging Face   │ │ 🚫 REJECT QUESTION  │
          │ AI MODEL       │ │                     │
          └───────┬────────┘ │ "Sorry, I am Dhan  │
                  │          │ Mitra Heart. I can  │
                  ▼          │ answer only finance│
          ┌────────────────┐ │ questions."        │
          │ 💚 FINANCE     │ └─────────────────────┘
          │ ANSWER         │
          └────────────────┘
```
""")

    st.markdown("### 🏗️ Technical Architecture")

    st.code("""
USER
  |
  v
STREAMLIT UI
  |
  +---- Station 1: Smart Wallet
  |          |
  |          +---- Wellness Score
  |
  +---- Station 2: Goal+
  |          |
  |          +---- Goal Timeline
  |
  +---- Station 3: Invest Smart
  |          |
  |          +---- Risk Profile
  |
  +---- Station 4: Wealth Lab
  |          |
  |          +---- Compound Growth
  |
  +---- Financial Context
             |
             v
       Finance Question Gate
          /           \
        YES            NO
         |              |
         v              v
  Dhan Mitra Prompt   Reject
         |
         v
  Hugging Face
  InferenceClient
         |
         v
  Finance-only answer
""", language="text")

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "💚 Dhan Mitra | Financial-literacy educational prototype | "
    "Projections are illustrations, not guarantees."
)

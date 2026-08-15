"""
Dhan Mitra — Station 5: AI Financial Coach
--------------------------------------------
This is the Station 5 deliverable: an AI financial coach chat, personalised
with data "gathered" from Stations 1-4. Since only Station 5 is being built
here, the sliders below act as a lightweight, self-contained simulator for
Stations 1-4 — a visitor drags a few sliders in each tab, and those numbers
flow straight into the AI coach's system prompt.

Run with:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

from config import (
    APP_TITLE, APP_TAGLINE, SPEND_CATEGORIES, GOAL_OPTIONS, RISK_QUESTIONS,
    RISK_TO_SUGGESTED_MIX, DEFAULT_RETURN_RATE, QUICK_PROMPTS,
    VAGUE_DEMO_PROMPT, DECLINE_MESSAGE, HF_MODEL_OPTIONS,
)
from utils import (
    compute_wellness_score, compute_goal_plan, compute_risk_score,
    compute_risk_profile, investment_comparison, compound_growth_series,
    future_value_sip,
)
from llm import build_system_prompt, get_client, ask_coach, looks_off_topic

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(page_title=APP_TITLE, page_icon="💰", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #f7f9fc 0%, #eef2f7 100%); }
    .dm-hero {
        background: linear-gradient(120deg, #0f2557 0%, #14532d 50%, #0f766e 100%);
        padding: 2rem 2.2rem; border-radius: 18px; color: white; margin-bottom: 1.3rem;
        box-shadow: 0 10px 30px rgba(15, 37, 87, 0.25);
    }
    .dm-hero h1 { margin: 0; font-size: 2.05rem; }
    .dm-hero p { margin: 0.35rem 0 0 0; opacity: 0.92; font-size: 1.05rem; }
    .dm-badge {
        display: inline-block; background: rgba(255,255,255,0.16);
        padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.8rem; margin-top: 0.7rem;
    }
    div.stButton > button {
        border-radius: 999px; border: 1px solid #0f766e; font-weight: 500;
    }
    div.stButton > button:hover { background-color: #0f766e; color: white; border-color: #0f766e; }
    .dm-callout {
        background: #ecfdf5; border: 1px solid #6ee7b7; border-radius: 12px;
        padding: 0.9rem 1.1rem; font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="dm-hero">
      <h1>💰 {APP_TITLE}</h1>
      <p>{APP_TAGLINE} — Station 5: Heart of Project</p>
      <span class="dm-badge">🤖 Powered by an open Hugging Face model</span>
    </div>
    """,
    unsafe_allow_html=True,
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


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------------------------------------------------------
# Sidebar — AI setup
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔑 AI Setup")
    hf_token = get_secret("HF_TOKEN")

    model_label = st.selectbox("Choose a model", list(HF_MODEL_OPTIONS.keys()))
    model_id = HF_MODEL_OPTIONS[model_label]

    with st.expander("Advanced settings"):
        custom_model = st.text_input("Custom model ID (optional)", value="")
        provider = st.text_input("Inference provider override (optional)", value="")
    if custom_model.strip():
        model_id = custom_model.strip()

    st.caption("🔗 Get a free token at huggingface.co/settings/tokens")
    st.divider()
    st.markdown("#### About")
    st.caption(APP_TAGLINE)
    st.caption("This build covers Station 5 only. Stations 1-4 below are a "
               "quick simulator so Station 5 has real numbers to personalise around.")

    if st.session_state.chat_history:
        if st.button("🗑️ Clear chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# ---------------------------------------------------------------------------
# Visitor profile builder — Stations 1-4 recap
# ---------------------------------------------------------------------------
st.markdown("## 🧩 Build Your Visitor Profile")
st.caption("Quick sliders standing in for Stations 1-4 — drag them, then chat with Station 5 below.")

tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Smart Wallet", "2️⃣ Goal+ Planner", "3️⃣ Invest Smart", "4️⃣ Wealth Lab",
])

# ---- Station 1: Smart Wallet ----------------------------------------------
with tab1:
    st.markdown("**Do you know where your money goes?**")
    income = st.slider("Monthly Income (₹)", min_value=5000, max_value=200000,
                        value=30000, step=1000, key="income")

    spends = {}
    cols = st.columns(3)
    for i, (cat, emoji, frac) in enumerate(SPEND_CATEGORIES):
        with cols[i % 3]:
            spends[cat] = st.slider(
                f"{emoji} {cat} (₹)", min_value=0, max_value=200000,
                value=int(income * frac), step=500, key=f"spend_{cat}",
            )

    wellness = compute_wellness_score(income, spends)

    if wellness["total_spend"] > income:
        st.warning("⚠️ You're spending more than you earn this month!")

    m1, m2, m3 = st.columns(3)
    m1.metric("Financial Wellness Score", f"{wellness['score']}/100", wellness["band"])
    m2.metric("Monthly Savings", f"₹{wellness['savings']:,.0f}", f"{wellness['savings_rate']}% of income")
    m3.metric("Total Monthly Spend", f"₹{wellness['total_spend']:,.0f}")
    st.progress(wellness["score"] / 100)

# ---- Station 2: Goal+ Planner ---------------------------------------------
with tab2:
    st.markdown("**Don't just save. Save with a purpose.**")
    goal_name = st.selectbox("Choose your goal", GOAL_OPTIONS, key="goal_name")
    target = st.slider("Target Amount (₹)", min_value=1000, max_value=1000000,
                        value=20000, step=500, key="goal_target")
    saved = st.slider("Already Saved So Far (₹)", min_value=0, max_value=500000,
                       value=2000, step=500, key="goal_saved")
    monthly_save = st.slider("You Can Save Monthly (₹)", min_value=100, max_value=20000,
                              value=2000, step=100, key="goal_monthly")

    goal_plan = compute_goal_plan(target, saved, monthly_save)
    progress = min(saved / target, 1.0) if target > 0 else 0

    st.progress(progress, text=f"₹{saved:,.0f} / ₹{target:,.0f} saved")
    g1, g2 = st.columns(2)
    g1.metric("Months to Reach Goal", f"{goal_plan['months']:.1f} mo")
    g2.metric(f"Save ₹{goal_plan['boost']:.0f} more/month →", f"{goal_plan['faster_months']:.1f} mo",
               f"{goal_plan['months_saved']:.1f} months faster")

# ---- Station 3: Invest Smart -----------------------------------------------
with tab3:
    st.markdown("**\"Which option suits YOU?\"** — answer honestly:")
    answers = []
    for i, q in enumerate(RISK_QUESTIONS):
        choice = st.radio(q["question"], list(q["options"].keys()), key=f"risk_{i}")
        answers.append(q["options"][choice])

    risk_score = compute_risk_score(answers)
    risk_profile = compute_risk_profile(risk_score)
    mix = RISK_TO_SUGGESTED_MIX[risk_profile]
    comparison = investment_comparison(monthly_save, 10)

    st.success(f"🧭 Your Risk Profile: **{risk_profile}**")

    c1, c2 = st.columns([1, 1.3])
    with c1:
        st.markdown("**Illustrative suggested mix**")
        mix_df = pd.DataFrame(list(mix.items()), columns=["Product", "Suggested %"]).set_index("Product")
        st.bar_chart(mix_df)
    with c2:
        st.markdown(f"**If you invested ₹{monthly_save:,.0f}/month for 10 years:**")
        cmp_df = pd.DataFrame(list(comparison.items()), columns=["Product", "Projected Value (₹)"]).set_index("Product")
        st.bar_chart(cmp_df)

    st.info(
        "💡 **SIP vs Mutual Fund isn't a real comparison.** A SIP is a *method* — "
        "investing a fixed amount every month. A Mutual Fund is a *product* — a "
        "pool of stocks/bonds managed by experts. You invest **in** a Mutual Fund "
        "**via** a SIP."
    )

# ---- Station 4: Wealth Lab --------------------------------------------------
with tab4:
    st.markdown("**\"Show me the numbers!\"** — the compound growth calculator.")
    w_monthly = st.slider("Monthly Investment (₹)", min_value=100, max_value=50000,
                           value=2000, step=100, key="wealth_monthly")
    w_years = st.slider("Number of Years", min_value=1, max_value=40, value=10, key="wealth_years")
    w_rate = st.slider("Assumed Annual Return (%)", min_value=1.0, max_value=20.0,
                        value=DEFAULT_RETURN_RATE, step=0.5, key="wealth_rate")

    fv = future_value_sip(w_monthly, w_years, w_rate / 100)
    fv_half = future_value_sip(w_monthly, w_years / 2, w_rate / 100)
    series = compound_growth_series(w_monthly, w_years, w_rate)

    st.caption("Example from Dhan Mitra's own story: ₹500/month at 12% ≈ ₹1,15,019 in 10 years, "
               "but ≈ ₹4,94,969 in 20 years — twice the time, ~4× the money.")

    v1, v2 = st.columns(2)
    v1.metric(f"Projected Value in {w_years} years", f"₹{fv:,.0f}")
    if fv_half > 0:
        v2.metric(f"...vs. just {w_years/2:.0f} years", f"₹{fv_half:,.0f}", f"{fv/fv_half:.1f}× less")

    chart_df = pd.DataFrame(series).set_index("year") if series else pd.DataFrame()
    if not chart_df.empty:
        st.line_chart(chart_df)

    st.markdown(
        f'<div class="dm-callout">📈 Twice the time isn\'t twice the money — it\'s roughly '
        f'<b>{(fv/fv_half if fv_half > 0 else 0):.1f}×</b> more, thanks to compounding. '
        f'Starting early is the single biggest lever you control.</div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Assemble the visitor profile for the AI
# ---------------------------------------------------------------------------
profile = {
    "station1": {
        "income": income,
        "total_spend": wellness["total_spend"],
        "savings_rate": wellness["savings_rate"],
        "score": wellness["score"],
        "band": wellness["band"],
    },
    "station2": {
        "goal_name": goal_name,
        "target": target,
        "saved": saved,
        "monthly": monthly_save,
        "months": goal_plan["months"],
        "faster_months": goal_plan["faster_months"],
        "boost": goal_plan["boost"],
    },
    "station3": {
        "risk_profile": risk_profile,
        "mix": mix,
        "comparison": comparison,
    },
    "station4": {
        "monthly": w_monthly,
        "years": w_years,
        "rate": w_rate,
        "future_value": round(fv),
    },
}
st.session_state.profile = profile

st.divider()

# ---------------------------------------------------------------------------
# Station 5 — AI Financial Coach
# ---------------------------------------------------------------------------
st.markdown("## 🤖 Station 5 — AI Financial Coach")
st.caption("Grand Finale — the heart of Dhan Mitra. Ask it anything about *your* money.")

p1, p2, p3, p4 = st.columns(4)
p1.metric("Wellness Score", f"{wellness['score']}/100")
p2.metric("Goal", goal_name.split(" ", 1)[-1])
p3.metric("Risk Profile", risk_profile)
p4.metric(f"{w_years}-yr Projection", f"₹{fv:,.0f}")


def send_message(user_text: str):
    if not hf_token:
        st.warning("👈 Please add your Hugging Face API token in the sidebar to chat.")
        return

    st.session_state.chat_history.append({"role": "user", "content": user_text})

    if looks_off_topic(user_text):
        reply = DECLINE_MESSAGE
    else:
        with st.spinner("Dhan Mitra AI is thinking..."):
            client = get_client(hf_token, provider or None)
            system_prompt = build_system_prompt(st.session_state.profile)
            reply = ask_coach(
                client, model_id, system_prompt,
                st.session_state.chat_history[:-1], user_text,
            )

    st.session_state.chat_history.append({"role": "assistant", "content": reply})


st.markdown("**💬 Quick prompts:**")
qcols = st.columns(3)
for i, qp in enumerate(QUICK_PROMPTS):
    if qcols[i % 3].button(qp, key=f"qp_{i}", use_container_width=True):
        send_message(qp)
        st.rerun()

st.markdown("")

if not st.session_state.chat_history:
    st.info("👋 Ask me about your Wellness Score, your goal timeline, SIPs, or how "
             "compounding grows your money — I'll answer using *your* numbers above.")

for msg in st.session_state.chat_history:
    avatar = "💰" if msg["role"] == "assistant" else "🧑"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask Dhan Mitra AI about your money...")
if user_input:
    send_message(user_input)
    st.rerun()

# ---------------------------------------------------------------------------
# Prompt Engineering demo
# ---------------------------------------------------------------------------
st.divider()
with st.expander("🎓 See Prompt Engineering in action — vague vs. personalised"):
    st.caption(
        "A generic financial FAQ bot vs. Dhan Mitra AI, asked the exact same "
        "question. Same underlying model — the difference is the prompt."
    )
    demo_prompt = st.text_input("Try a deliberately vague question", value=VAGUE_DEMO_PROMPT)

    if st.button("Compare responses"):
        if not hf_token:
            st.warning("👈 Please add your Hugging Face API token in the sidebar first.")
        else:
            client = get_client(hf_token, provider or None)
            generic_system = (
                "You are a generic financial FAQ assistant. Answer briefly and "
                "generically, with no personalisation, in under 80 words."
            )
            personal_system = build_system_prompt(st.session_state.profile)

            dc1, dc2 = st.columns(2)
            with dc1:
                st.markdown("**❌ Vague prompt → generic bot**")
                with st.spinner("Thinking..."):
                    generic_reply = ask_coach(client, model_id, generic_system, [], demo_prompt)
                st.info(generic_reply)
            with dc2:
                st.markdown("**✅ Same question → Dhan Mitra AI (personalised)**")
                with st.spinner("Thinking..."):
                    personal_reply = ask_coach(client, model_id, personal_system, [], demo_prompt)
                st.success(personal_reply)

st.divider()
st.caption(
    "⚠️ Dhan Mitra is a student-built educational exhibit. All figures are "
    "illustrative estimates, not real financial, tax, or investment advice."
)

"""
Dhan Mitra — Station 5: AI Financial Coach
Shared configuration, constants and copy used across the app.
"""

APP_TITLE = "Dhan Mitra AI Financial Coach"
APP_TAGLINE = "Your Smart Friend for Every Financial Decision"

# ---------------------------------------------------------------------------
# Station 1 — Smart Wallet  (name, emoji, default share of income)
# ---------------------------------------------------------------------------
SPEND_CATEGORIES = [
    ("Housing / Rent", "🏠", 0.28),
    ("Food & Groceries", "🍲", 0.15),
    ("Transport", "🚌", 0.08),
    ("Utilities & Bills", "💡", 0.07),
    ("Entertainment & Lifestyle", "🎬", 0.06),
    ("Other / Miscellaneous", "🧾", 0.05),
]

# ---------------------------------------------------------------------------
# Station 2 — Goal+ Planner
# ---------------------------------------------------------------------------
GOAL_OPTIONS = [
    "📱 New Phone",
    "💻 Laptop",
    "🏍️ Bike",
    "✈️ Vacation Trip",
    "🎓 Higher Education",
    "🛟 Emergency Fund",
    "🎯 Custom Goal",
]

# ---------------------------------------------------------------------------
# Station 3 — Invest Smart
# ---------------------------------------------------------------------------
RISK_QUESTIONS = [
    {
        "question": "If your investment suddenly dropped 15% in value, what would you do?",
        "options": {
            "Sell immediately to avoid further loss": 1,
            "Feel worried, but wait and watch": 2,
            "Stay calm — it's part of the journey": 3,
            "Invest more — it's a discount!": 4,
        },
    },
    {
        "question": "How long can you keep this money invested without needing it back?",
        "options": {
            "Less than 1 year": 1,
            "1 – 3 years": 2,
            "3 – 7 years": 3,
            "7+ years": 4,
        },
    },
    {
        "question": "Which sounds most like you?",
        "options": {
            "I want my money 100% safe, even for lower returns": 1,
            "I want steady, predictable growth": 2,
            "I'm okay with ups and downs for better growth": 3,
            "I chase the highest possible growth — risk doesn't scare me": 4,
        },
    },
]

# inclusive (low, high) total-score ranges -> risk profile label
RISK_PROFILES = {
    (3, 5): "Conservative",
    (6, 8): "Moderate",
    (9, 11): "Growth-Oriented",
    (12, 12): "Aggressive",
}

# Illustrative long-term annual return assumptions (educational, NOT guarantees)
INVESTMENT_ASSUMPTIONS = {
    "Fixed Deposit (FD)": 0.065,
    "Gold": 0.08,
    "Mutual Funds (via SIP)": 0.12,
    "Stocks (Direct Equity)": 0.15,
}

RISK_TO_SUGGESTED_MIX = {
    "Conservative": {"Fixed Deposit (FD)": 60, "Gold": 25, "Mutual Funds (via SIP)": 15, "Stocks (Direct Equity)": 0},
    "Moderate": {"Fixed Deposit (FD)": 35, "Gold": 15, "Mutual Funds (via SIP)": 40, "Stocks (Direct Equity)": 10},
    "Growth-Oriented": {"Fixed Deposit (FD)": 15, "Gold": 10, "Mutual Funds (via SIP)": 50, "Stocks (Direct Equity)": 25},
    "Aggressive": {"Fixed Deposit (FD)": 5, "Gold": 5, "Mutual Funds (via SIP)": 45, "Stocks (Direct Equity)": 45},
}

# ---------------------------------------------------------------------------
# Station 4 — Wealth Lab
# ---------------------------------------------------------------------------
DEFAULT_RETURN_RATE = 12.0

# ---------------------------------------------------------------------------
# Station 5 — AI Financial Coach
# ---------------------------------------------------------------------------
QUICK_PROMPTS = [
    "📊 Explain my Wellness Score simply",
    "🎯 How can I reach my goal faster?",
    "⚖️ FD vs Mutual Fund — what suits me?",
    "🔁 What's the real difference between SIP and a Mutual Fund?",
    "📈 Show me why starting early matters",
    "💡 Give me one money habit to start this month",
]

VAGUE_DEMO_PROMPT = "How do I grow my money?"

DECLINE_MESSAGE = (
    "I'm Dhan Mitra AI — your dedicated financial coach, so I can only help with "
    "money, saving, budgeting, investing and financial-planning questions. 😊 "
    "Ask me something about your finances — like your Wellness Score, your goal, "
    "or how to grow your savings — and I'll gladly help!"
)

# Local fast-path keywords: obviously unrelated topics get an instant, free
# decline without calling the model at all (saves API quota + latency). The
# system prompt below is the real guardrail — this is just a cheap first net.
OFF_TOPIC_FAST_PATH = [
    "weather", "cricket score", "football score", "ipl score", "movie review",
    "song lyrics", "who is the prime minister", "who is the president",
    "write code", "write a python", "debug my code", "homework answer",
    "capital of", "translate this", "write an essay on", "recipe for",
    "tell me a joke", "riddle", "who will win the match", "election result",
    "generate an image", "write a poem about love", "meaning of life",
]

# Models available via Hugging Face's serverless Inference Providers.
# Students can pick whichever is live/fastest on the day of the exhibit.
HF_MODEL_OPTIONS = {
    "Qwen 2.5 — 7B Instruct (recommended)": "Qwen/Qwen2.5-7B-Instruct", 
    "Qwen 2.5 — 1.5B Instruct (faster / lighter)": "Qwen/Qwen2.5-1.5B-Instruct",
    "Meta Llama 3.1 — 8B Instruct": "meta-llama/Llama-3.1-8B-Instruct",
}

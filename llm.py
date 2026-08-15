"""
Dhan Mitra — Station 5 LLM layer.
Wraps the Hugging Face Inference API (OpenAI-style chat completions) and
builds a profile-aware, guard-railed system prompt for the AI Financial Coach.
"""
from config import DECLINE_MESSAGE, OFF_TOPIC_FAST_PATH


def _fmt(value):
    return "N/A" if value is None else value


def looks_off_topic(message: str) -> bool:
    """Cheap local fast-path: catches obviously non-finance asks without
    spending an API call. The system prompt below is the *real* guardrail —
    this is just a free first line of defence for very obvious cases."""
    text = message.lower()
    return any(phrase in text for phrase in OFF_TOPIC_FAST_PATH)


def build_system_prompt(profile: dict) -> str:
    """Turns the visitor's Station 1-4 data into a personalised system prompt."""
    s1 = profile.get("station1", {})
    s2 = profile.get("station2", {})
    s3 = profile.get("station3", {})
    s4 = profile.get("station4", {})

    lines = [
        "You are 'Dhan Mitra AI' — a warm, encouraging, plain-language personal "
        "finance coach built for a student-run financial-literacy exhibit called "
        "Dhan Mitra ('Your Smart Friend for Every Financial Decision').",
        "",
        "You are talking to a visitor who has already walked through four stations "
        "of the exhibit. Use THEIR OWN numbers below whenever it makes an answer "
        "more concrete — that personalisation is the entire point of this station. "
        "Do not just repeat the numbers back at them; use them to reason and advise.",
        "",
        "--- VISITOR PROFILE ---",
    ]

    if s1:
        lines.append(
            f"Station 1 (Smart Wallet): monthly income Rs.{s1.get('income', 0):,.0f}, "
            f"monthly spend Rs.{s1.get('total_spend', 0):,.0f}, "
            f"savings rate {s1.get('savings_rate', 0)}%, "
            f"Financial Wellness Score {s1.get('score', '-')}/100 ({s1.get('band', '-')})."
        )
    if s2:
        lines.append(
            f"Station 2 (Goal+ Planner): goal '{s2.get('goal_name', '-')}', "
            f"target Rs.{s2.get('target', 0):,.0f}, already saved Rs.{s2.get('saved', 0):,.0f}, "
            f"saving Rs.{s2.get('monthly', 0):,.0f}/month -> reaches the goal in "
            f"{_fmt(s2.get('months'))} months (or just {_fmt(s2.get('faster_months'))} months "
            f"if they save Rs.{s2.get('boost', 0):,.0f} more per month)."
        )
    if s3:
        lines.append(
            f"Station 3 (Invest Smart): risk profile = {s3.get('risk_profile', '-')}. "
            f"Suggested illustrative portfolio mix: {s3.get('mix', {})}. "
            f"If they invested their monthly savings for 10 years, projected value by "
            f"product: {s3.get('comparison', {})}."
        )
    if s4:
        lines.append(
            f"Station 4 (Wealth Lab): investing Rs.{s4.get('monthly', 0):,.0f}/month for "
            f"{s4.get('years', 0)} years at an assumed {s4.get('rate', 0)}% annual return "
            f"projects to roughly Rs.{s4.get('future_value', 0):,.0f}."
        )

    lines += [
        "--- END PROFILE ---",
        "",
        "STYLE: Keep answers short (roughly 80-180 words unless the visitor explicitly "
        "asks for more detail), warm, practical and jargon-free — explain any financial "
        "term the moment you use it. Use 'Rs.' for currency. Use at most 1-2 emoji. "
        "Prefer short paragraphs or a tight bullet list over long essays.",
        "",
        "IMPORTANT EDUCATIONAL POINT: if SIP or Mutual Funds come up, always make clear "
        "that a SIP is a *method* of investing (a fixed amount every month) while a "
        "Mutual Fund is the *product* being invested in — you invest IN a mutual fund VIA "
        "a SIP. Never present 'SIP vs Mutual Fund' as a real, like-for-like comparison.",
        "",
        "All figures you use or generate are educational estimates for a school exhibit, "
        "not real financial advice or guaranteed returns. If a question asks for something "
        "that sounds like real trading, tax, or legal advice, explain the general concept "
        "and gently note that a real licensed advisor should be consulted for actual decisions.",
        "",
        "STRICT SCOPE — READ CAREFULLY: you ONLY discuss personal finance: budgeting, "
        "saving, goals, investing, SIPs, mutual funds, stocks, gold, FDs, loans, credit, "
        "insurance, taxes, retirement, and this Dhan Mitra exhibit. If the visitor asks "
        "about anything else at all (coding help, homework, general trivia, current "
        "events, entertainment, relationships, medical or legal advice unrelated to "
        "money, etc.), do NOT answer it in any way — politely decline using words to "
        f"this effect: \"{DECLINE_MESSAGE}\" — and invite them to ask a finance question "
        "instead. Never partially answer an off-topic question before declining.",
    ]

    return "\n".join(lines)


def get_client(token: str, provider: str = None):
    from huggingface_hub import InferenceClient
    if provider:
        return InferenceClient(token=token, provider=provider)
    return InferenceClient(token=token)


def ask_coach(client, model: str, system_prompt: str, chat_history: list, user_message: str) -> str:
    """chat_history: list of {'role': 'user'|'assistant', 'content': str}"""
    messages = [{"role": "system", "content": system_prompt}]
    messages += chat_history
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat_completion(
            messages=messages,
            model=model,
            max_tokens=500,
            temperature=0.6,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:  # noqa: BLE001 - surface any provider/model error to the UI
        return (
            "⚠️ I couldn't reach the AI model right now "
            f"({exc.__class__.__name__}: {exc}). Please check your Hugging Face "
            "token, try a different model in the sidebar, or try again shortly."
        )

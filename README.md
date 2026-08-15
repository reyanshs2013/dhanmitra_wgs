# Dhan Mitra — Station 5: AI Financial Coach

A Streamlit app for **Station 5 only** of the Dhan Mitra exhibit — the AI
Financial Coach chat, personalised with data "gathered" from Stations 1-4
and powered by an open Hugging Face model (Qwen 2.5 by default).

## What's inside

| File | Purpose |
|---|---|
| `app.py` | The Streamlit UI — profile-builder sliders + Station 5 chat |
| `config.py` | All copy, categories, quick prompts, guardrail keywords, model list |
| `utils.py` | The maths: Wellness Score, goal timeline, SIP compounding, risk profile |
| `llm.py` | Hugging Face `InferenceClient` wrapper, personalised system-prompt builder, finance-only guardrail |
| `requirements.txt` | Python dependencies |

Since only Station 5 is being built here, the **"Build Your Visitor
Profile" tabs act as a stand-in for Stations 1-4** — a visitor drags a
few sliders (income & spending, a savings goal, a 3-question risk quiz,
and a compounding calculator), and those exact numbers are threaded into
the AI coach's system prompt below, so its answers are genuinely
personalised rather than generic.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get a free Hugging Face token**
   Go to <https://huggingface.co/settings/tokens> → "New token" → enable
   **"Make calls to Inference Providers"**. Copy the token (starts with `hf_`).

3. **Run the app**
   ```bash
   streamlit run app.py
   ```

4. In the sidebar, paste your token and pick a model (Qwen 2.5 7B
   Instruct is selected by default). If a model isn't available via the
   free Inference Providers on a given day, just switch the dropdown to
   another one, or paste a custom model ID under "Advanced settings".

5. Drag the sliders in the four tabs, then chat with the coach at the
   bottom of the page — try the quick-prompt buttons, or type your own
   question.

## How the guardrail works ("finance questions only")

Two layers, both implemented in `llm.py`:

1. **Fast local pre-check** (`looks_off_topic`) — a small keyword list
   catches obviously unrelated asks (weather, sports scores, "write my
   code", trivia, etc.) and replies instantly with a polite decline —
   *without* spending an API call.
2. **System-prompt instruction** — every real call to the model is sent
   a strict "STRICT SCOPE" instruction telling it to only discuss
   personal finance, and to politely decline (with a fixed template)
   anything else, without partially answering first.

## The Prompt Engineering demo

At the bottom of the page, an expander lets you type one vague question
and see it answered twice with the *same* model: once by a plain,
un-personalised system prompt, and once by Dhan Mitra's full
personalised prompt — a live demonstration of why prompt engineering
(not just "having an AI") is Station 5's real differentiator.

## Notes

- All financial figures (Wellness Score, projected returns, goal
  timelines) are simplified, illustrative calculations for a school
  exhibit — not real financial, tax, or investment advice.
- The four "station" tabs recompute live as you move sliders; there's
  no separate save step — whatever the sliders show is what the AI
  coach sees.

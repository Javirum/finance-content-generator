"""MoneySavy AI — Streamlit Web UI for the finance content generator."""

import os

import streamlit as st

from src.llm_client import get_client, get_last_usage_stats
from src.knowledge_base import KnowledgeBase
from src.prompts import PromptManager
from src.generator import generate_daily_content, save_output, OUTPUT_DIR
from src.usage_tracker import get_monthly_summary

KB_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ── Initialise session state ────────────────────────────────────────────────

def init_state():
    if "client" not in st.session_state:
        st.session_state.client = get_client()
    if "kb" not in st.session_state:
        kb = KnowledgeBase(KB_DIR, openai_client=st.session_state.client)
        kb.load_all()
        st.session_state.kb = kb
    if "prompt_mgr" not in st.session_state:
        st.session_state.prompt_mgr = PromptManager()
    if "generated_content" not in st.session_state:
        st.session_state.generated_content = ""


init_state()

kb: KnowledgeBase = st.session_state.kb
client = st.session_state.client
prompt_mgr: PromptManager = st.session_state.prompt_mgr


# ── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="MoneySavy AI", page_icon="💰", layout="wide")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════

st.title("💰 MoneySavy AI")
st.header("🐦 Content Generator")

col_topic, col_day = st.columns([3, 2])

topic = col_topic.text_input("Topic", placeholder="e.g. first paycheck tips")
weekday = col_day.selectbox("Day", WEEKDAYS)

if st.button("Generate", type="primary", disabled=not topic):
    with st.spinner("Generating..."):
        result = generate_daily_content(client, kb, prompt_mgr, topic, weekday)
        st.session_state.generated_content = result
        st.session_state.usage_stats = get_last_usage_stats()

# ── Output display ──────────────────────────────────────────────────────────

content = st.session_state.generated_content
if content:
    st.subheader("Output")
    st.markdown(f"```\n{content}\n```")

    # ── Usage stats ──────────────────────────────────────────────────────
    stats = st.session_state.get("usage_stats")
    if stats:
        with st.expander("Token usage & cost"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Input tokens", f"{stats['input_tokens']:,}")
            c2.metric("Cached", f"{stats['cached_tokens']:,}")
            c3.metric("Cache hit", f"{stats['cache_hit_pct']:.0f}%")
            c4.metric("Cost", f"${stats['cost_usd']:.4f}")

    col_copy, col_save_btn = st.columns(2)
    if col_save_btn.button("Save to file"):
        path = save_output(content, topic)
        st.success(f"Saved → {os.path.relpath(path)}")

# ── Monthly usage ──────────────────────────────────────────────────────

st.divider()

monthly = get_monthly_summary()
st.subheader("Monthly Usage ({})".format(monthly["month"]))

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Requests", monthly["requests"])
m2.metric("Input tokens", "{:,}".format(monthly["input_tokens"]))
m3.metric("Output tokens", "{:,}".format(monthly["output_tokens"]))
m4.metric("Avg cache hit", "{:.0f}%".format(monthly["avg_cache_hit_pct"]))
m5.metric("Total cost", "${:.4f}".format(monthly["total_cost_usd"]))

# ── History ─────────────────────────────────────────────────────────────────

st.divider()

with st.expander("📜 History (saved outputs)"):
    if os.path.isdir(OUTPUT_DIR):
        files = sorted(os.listdir(OUTPUT_DIR), reverse=True)
        if files:
            for fname in files:
                fpath = os.path.join(OUTPUT_DIR, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    st.markdown(f"**{fname}**")
                    st.code(f.read())
        else:
            st.info("No saved outputs yet.")
    else:
        st.info("No saved outputs yet.")

"""MoneySavvy AI — Streamlit Web UI for the finance content generator."""

import os
import tempfile

import streamlit as st

from src.llm_client import get_client
from src.knowledge_base import KnowledgeBase
from src.prompts import PromptManager, SYSTEM_PROMPT_PATH
from src.generator import generate_tweet, generate_thread, save_output, OUTPUT_DIR

KB_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")


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

st.set_page_config(page_title="MoneySavvy AI", page_icon="💰", layout="wide")


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("💰 MoneySavvy AI")

    # ── Knowledge Base ──────────────────────────────────────────────────────

    st.header("📂 Knowledge Base")

    entries = kb.list_entries()
    total_kb = sum(e.size_kb for e in entries)
    st.caption(f"{len(entries)} file{'s' if len(entries) != 1 else ''} · {total_kb:.1f} KB")

    for idx, entry in enumerate(entries, 1):
        col_name, col_btn = st.columns([4, 1])
        col_name.text(f"{entry.name} ({entry.fmt})")
        if col_btn.button("✕", key=f"rm_{idx}"):
            kb.remove(idx)
            st.rerun()

    # Upload files
    uploaded = st.file_uploader(
        "Upload files",
        accept_multiple_files=True,
        type=["md", "txt", "pdf", "docx", "mp3", "wav", "m4a", "ogg"],
    )
    if uploaded:
        for f in uploaded:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{f.name}")
            tmp.write(f.read())
            tmp.close()
            try:
                kb.add(tmp.name)
            except Exception as e:
                st.error(f"Error adding {f.name}: {e}")
            finally:
                os.unlink(tmp.name)
        st.rerun()

    # YouTube URL
    yt_url = st.text_input("YouTube URL")
    if st.button("Add YouTube") and yt_url:
        try:
            kb.add(yt_url)
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()

    # ── System Prompt ───────────────────────────────────────────────────────

    st.header("📝 System Prompt")

    edited_prompt = st.text_area(
        "Edit system prompt",
        value=prompt_mgr.system_prompt,
        height=200,
        label_visibility="collapsed",
    )

    col_save, col_reset = st.columns(2)
    if col_save.button("Save Prompt"):
        with open(SYSTEM_PROMPT_PATH, "w", encoding="utf-8") as f:
            f.write(edited_prompt)
        prompt_mgr._load()
        st.success("Saved!")

    if col_reset.button("Reset to Default"):
        prompt_mgr.reset()
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════

st.header("🐦 Content Generator")

col_topic, col_style, col_count = st.columns([3, 2, 2])

topic = col_topic.text_input("Topic", placeholder="e.g. first paycheck tips")
style = col_style.selectbox("Style", ["educational", "motivational", "myth-busting"])
tweet_count = col_count.slider("Number of tweets", min_value=1, max_value=5, value=1)

if st.button("Generate", type="primary", disabled=not topic):
    with st.spinner("Generating..."):
        if tweet_count == 1:
            result = generate_tweet(client, kb, prompt_mgr, topic, style)
        else:
            result = generate_thread(client, kb, prompt_mgr, topic, style, count=tweet_count)
        st.session_state.generated_content = result

# ── Output display ──────────────────────────────────────────────────────────

content = st.session_state.generated_content
if content:
    st.subheader("Output")
    st.markdown(f"```\n{content}\n```")

    if tweet_count == 1:
        length = len(content)
        color = "green" if length <= 280 else "red"
        st.markdown(f":{color}[{length} / 280 characters]")

    col_copy, col_save_btn = st.columns(2)
    if col_save_btn.button("Save to file"):
        path = save_output(content, topic)
        st.success(f"Saved → {os.path.relpath(path)}")

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

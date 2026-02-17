# LazyInvest — Gen Z Financial Coach Content Engine

## Technical Project Plan (2-Day Build)

---

## 1. Project Overview

**What:** An AI-powered content generation system that produces brand-aligned financial education tweets targeting Gen Z (17–23, Europe-based).

**Why:** Convert financial education into trust and referrals by speaking Gen Z's language about real money situations (first paycheck, rent, subscriptions, saving for travel, ETF curiosity).

**MVP Output:** Generate tweets for X that are educational, brand-consistent, and clearly differentiated from generic AI content.

**Funnel:** Education → Trust → Referral

---

## 2. Architecture

```
┌─────────────────────────────────────────────────┐
│            Interactive CLI Session               │
│                                                  │
│  STARTUP:                                        │
│  1. Load all KB files (primary + secondary)      │
│  2. Display loaded files list to user            │
│                                                  │
│  INTERACTIVE LOOP:                               │
│  ┌─────────────────────────────────────────┐     │
│  │  > list         — show loaded KB files  │     │
│  │  > add <path>   — add a file to KB      │     │
│  │  > remove <#>   — remove a file from KB │     │
│  │  > prompt       — show current system   │     │
│  │                    prompt               │     │
│  │  > prompt edit  — edit system prompt     │     │
│  │                    in default editor     │     │
│  │  > prompt reset — restore default        │     │
│  │                    system prompt         │     │
│  │  > generate     — generate content      │     │
│  │  > quit         — exit                  │     │
│  └─────────────────────────────────────────┘     │
└──────────────────────┬──────────────────────────┘
                       │
          (on "generate" command)
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              Content Generator Engine            │
│                                                  │
│  1. Use already-loaded KB context (in memory)    │
│  2. Build context-aware prompt                   │
│  3. Call LLM API                                 │
│  4. Post-process & validate output               │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
                ┌──────────────────────┐
                │   LLM API            │
                │   (OpenAI GPT)       │
                └──────────────────────┘
```

### Core Components

| Component | File | Responsibility |
|---|---|---|
| File Processor | `src/file_processor.py` | Detect file type and extract text (PDF, audio, TXT, MD, DOCX, YouTube) |
| Knowledge Base Manager | `src/knowledge_base.py` | Load KB files once at startup via File Processor, hold in memory, support add/remove at runtime |
| Prompt Manager | `src/prompts.py` | Load system prompt from file on startup, persist edits to disk, assemble final prompt with KB context |
| LLM Client | `src/llm_client.py` | Call OpenAI API, handle responses and errors |
| Content Generator | `src/generator.py` | Orchestrate: read KB from memory → build prompt → call LLM → format output |
| Interactive CLI | `main.py` | Interactive session: list/add/remove KB files, trigger generation |

---

## 3. Project Structure

```
finance-content-generator/
├── main.py                          # Entry point / CLI
├── .env                             # API keys (gitignored)
├── .gitignore
├── requirements.txt
├── PROJECT_PLAN.md
│
├── src/
│   ├── __init__.py
│   ├── file_processor.py            # Multi-format file parser (PDF, audio, TXT, MD, DOCX, YouTube)
│   ├── knowledge_base.py            # KB manager (load, list, add, remove)
│   ├── prompts.py                   # Prompt templates and assembly
│   ├── llm_client.py                # OpenAI API wrapper
│   └── generator.py                 # Main orchestration logic
│
├── prompts/
│   ├── system_prompt.md             # Active system prompt (persisted, user-editable)
│   ├── system_prompt.default.md     # Default system prompt (used by "prompt reset")
│   └── templates/
│       ├── tweet_single.md          # Template: single tweet
│       └── tweet_thread.md          # Template: tweet thread
│
├── knowledge_base/
│   ├── primary/
│   │   ├── brand-guidelines.md      # Tone, voice, dos/don'ts
│   │   ├── bank-statements.md       # Simulated spending/income data
│   │   ├── content-examples.md      # Past content samples
│   │   └── genz-language.md         # Slang, phrasing, communication style
│   │
│   └── secondary/
│       ├── genz_research.md         # Financial behavior research
│       ├── genz_patterns.md         # Common behavioral patterns
│       ├── common_money_traps.md    # Subscriptions, BNPL, impulse spending
│       ├── investing_basics.md      # ETF basics, time horizon, diversification
│       ├── market_context.md        # Current economic situation (EU focus)
│       └── competitor_analysis.md   # Germany & Spain landscape
│
└── output/
    └── generated/                   # Saved generated content
```

---

## 4. Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.11+ | Fast prototyping, great LLM ecosystem |
| LLM API | OpenAI GPT-4o | Strong instruction following, good at voice/tone |
| PDF Parsing | `PyPDF2` | Lightweight, pure Python, no system dependencies |
| Audio Transcription | OpenAI Whisper API | Already have OpenAI key, high-quality transcription |
| Word Documents | `python-docx` | Standard `.docx` parsing |
| YouTube Transcripts | `youtube-transcript-api` | Extract subtitles/transcripts from YouTube URLs |
| Config / Secrets | `python-dotenv` | Load API keys from `.env` |
| CLI | `argparse` (stdlib) | No extra dependency needed for MVP |

### Supported File Formats

| Format | Extensions / Input | Processing Method |
|---|---|---|
| Markdown | `.md` | Read as plain text |
| Plain text | `.txt` | Read as plain text |
| PDF | `.pdf` | Extract text via `PyPDF2` |
| Word | `.docx` | Extract text via `python-docx` |
| Audio | `.mp3`, `.wav`, `.m4a`, `.ogg` | Transcribe via OpenAI Whisper API |
| YouTube | YouTube URL | Fetch transcript via `youtube-transcript-api` |

### Dependencies (`requirements.txt`)

```
openai>=1.0.0
python-dotenv>=1.0.0
PyPDF2>=3.0.0
python-docx>=1.0.0
youtube-transcript-api>=0.6.0
```

---

## 5. Day-by-Day Breakdown

### DAY 1 — Foundation & Core Implementation

#### Morning (3–4 hours): Setup + Knowledge Base

| # | Task | Output |
|---|---|---|
| 1.1 | Initialize project (git init, folder structure, `.gitignore`, `.env`) | Scaffolded repo |
| 1.2 | Install dependencies (`pip install openai python-dotenv PyPDF2 python-docx youtube-transcript-api`) | Working env |
| 1.3 | Write **primary knowledge base** documents | `knowledge_base/primary/` populated |
| | - `brand-guidelines.md`: tone (friendly, simple, non-judgmental, practical), voice rules, dos/don'ts | |
| | - `bank-statements.md`: simulated income/expenses for a 20-year-old in EU | |
| | - `content-examples.md`: 5–10 example tweets/posts in target voice | |
| | - `genz-language.md`: common phrases, slang, communication patterns | |
| 1.4 | Write **secondary knowledge base** documents (2–3 docs) | `knowledge_base/secondary/` populated |
| | - `genz_patterns.md`: paycheck-to-paycheck, impulse spending, low savings confidence | |
| | - `common_money_traps.md`: subscriptions stacking, BNPL, lifestyle creep | |
| | - `investing_basics.md`: ETF intro, compound interest, time horizon | |

#### Afternoon (3–4 hours): Core Development

| # | Task | Output |
|---|---|---|
| 1.5 | Implement `src/file_processor.py` | Detect file type by extension/URL, extract text from each format (MD, TXT, PDF, DOCX, audio, YouTube) |
| 1.6 | Implement `src/knowledge_base.py` | Load all KB files once via file processor, display list, support add/remove at runtime |
| 1.7 | Create `prompts/system_prompt.default.md` and tweet templates | Default system prompt with brand role + rules; `tweet_single.md` with tweet generation instructions |
| 1.8 | Implement `src/prompts.py` | Load system prompt from disk on startup, support view/edit/reset, assemble final prompt with KB context |
| 1.9 | Implement `src/llm_client.py` | Thin wrapper: takes messages, calls OpenAI GPT-4o, returns text |
| 1.10 | Implement `src/generator.py` | Ties it all together: load KB → build prompt → call LLM → return content |
| 1.11 | Build `main.py` interactive CLI | `python main.py` starts session → loads KB → user can list/add/remove files, then `generate --topic "first paycheck"` |
| 1.12 | Test end-to-end: generate first tweet | Working MVP |

### DAY 2 — Refinement, Quality & Polish

#### Morning (3–4 hours): Content Quality

| # | Task | Output |
|---|---|---|
| 2.1 | Refine system prompt based on Day 1 outputs | Better brand alignment |
| 2.2 | Add topic/scenario selection (predefined list of Gen Z situations) | `--topic` picks from real scenarios |
| 2.3 | Add tweet thread generation (`tweet_thread.md` template) | Can generate 3–5 tweet threads |
| 2.4 | Add output saving to `output/generated/` with timestamps | Persistent content log |
| 2.5 | Add remaining secondary KB docs (`market_context.md`, `competitor_analysis.md`) | Fuller context |

#### Afternoon (3–4 hours): Differentiation & Demo

| # | Task | Output |
|---|---|---|
| 2.6 | Add batch generation (multiple tweets per run) | `--count 5` flag |
| 2.7 | Add content variation controls (educational / motivational / myth-busting) | `--style` flag |
| 2.8 | Side-by-side comparison: generic vs brand-aligned output | Demo-ready proof of differentiation |
| 2.9 | Generate sample content library (10–15 tweets across topics) | Portfolio of outputs |
| 2.10 | Final README + demo prep | Presentable project |

---

## 6. Key Design Decisions

### Prompt Strategy (3-Layer)

```
┌─────────────────────────────────────┐
│  SYSTEM PROMPT (from disk)          │
│  - Loaded from system_prompt.md     │
│  - Editable via "prompt edit"       │
│  - Brand voice rules                │
│  - Target audience definition       │
│  - Content rules (no jargon, etc.)  │
├─────────────────────────────────────┤
│  CONTEXT (from Knowledge Base)      │
│  - Relevant brand guidelines        │
│  - Gen Z financial patterns         │
│  - Real spending examples           │
│  - Past content samples             │
├─────────────────────────────────────┤
│  USER REQUEST                       │
│  - Topic / scenario                 │
│  - Content type (tweet / thread)    │
│  - Style (educational / motivation) │
└─────────────────────────────────────┘
```

### Knowledge Base Loading Strategy

- **Load once at startup** — all files from `knowledge_base/primary/` and `knowledge_base/secondary/` are read into memory
- **Display loaded files** — on startup, print a numbered list so the user sees exactly what context the LLM will use:
  ```
  📂 Knowledge Base loaded (9 files):
   [1] primary/brand-guidelines.md        (MD)     1.2 KB
   [2] primary/bank-statements.pdf        (PDF)    0.8 KB
   [3] primary/content-examples.md        (MD)     0.6 KB
   [4] primary/genz-language.md           (MD)     0.5 KB
   [5] secondary/genz_patterns.md         (MD)     0.9 KB
   [6] secondary/common_money_traps.md    (MD)     0.7 KB
   [7] secondary/investing_basics.md      (MD)     1.1 KB
   [8] secondary/interview.mp3            (AUDIO)  2.3 KB  ← transcribed via Whisper
   [9] secondary/competitor_analysis.docx  (DOCX)   0.8 KB
  ```
- **User can manage KB at runtime:**
  - `list` — re-display the current loaded files with format and size
  - `add <filepath|URL>` — load a new file into memory; auto-detects format (`.md`, `.txt`, `.pdf`, `.docx`, `.mp3/.wav/.m4a/.ogg`, or YouTube URL)
  - `remove <#>` — unload a file by its number (removes from memory, does NOT delete from disk)
- **All loaded files** are included as context on every generation (no selective loading)
- Keep total context under ~4000 tokens to leave room for generation — warn the user if the KB gets too large

### System Prompt Persistence

- **Saved to disk** at `prompts/system_prompt.md` — loaded automatically on every session start, no need to re-enter it
- **Default backup** at `prompts/system_prompt.default.md` — ships with the project, never modified by the app
- **On first run:** if `system_prompt.md` doesn't exist, copy from `system_prompt.default.md`
- **User commands:**
  - `prompt` — display the current system prompt in the terminal
  - `prompt edit` — open `prompts/system_prompt.md` in the user's default text editor (`$EDITOR` or fallback to `nano`/`notepad`); changes are saved to disk and reloaded into memory when the editor closes
  - `prompt reset` — overwrite `system_prompt.md` with `system_prompt.default.md` and reload into memory
- **Every `generate` call** uses whatever is currently in memory (which always matches what's on disk)

### Content Validation Rules (Post-Processing)

- Tweet must be ≤ 280 characters
- No financial advice disclaimers in the tweet itself (handle separately)
- Must match brand tone checklist (no jargon, no condescension, practical)
- Must reference a real Gen Z scenario

---

## 7. Default System Prompt (`prompts/system_prompt.default.md`)

```markdown
You are LazyInvest, a financial coach for Gen Z (17–23, Europe-based).

## Your Voice
- Friendly, like a smart older sibling who's good with money
- Simple language — no finance jargon unless you explain it
- Non-judgmental — never shame spending habits
- Practical — every tip must be actionable TODAY

## Your Audience
- First job, first paycheck, first real financial decisions
- Deals with: rent/WG, subscriptions (Spotify, Netflix), eating out, clubbing
- Curious about saving and maybe investing (ETFs)
- Skeptical of traditional finance advice
- Lives on social media, communicates in short bursts

## Content Rules
- Always tie advice to a real situation they face
- Use "you" language, not "one should"
- One clear takeaway per tweet
- Allowed: light humor, relatable references, mild slang
- Never: condescending tone, unrealistic advice, generic platitudes
```

---

## 8. Success Criteria for MVP

| Criteria | Metric |
|---|---|
| Functional | Can generate a tweet from CLI with a topic input |
| Brand-aligned | Output follows brand guidelines (manual review) |
| Differentiated | Side-by-side with generic ChatGPT output shows clear difference |
| Knowledge-grounded | Content references real Gen Z scenarios from KB |
| Reproducible | Different runs with same topic produce varied but on-brand content |

---

## 9. Environment Setup (Quick Start)

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install openai python-dotenv PyPDF2 python-docx youtube-transcript-api

# 3. Set up API key
echo "OPENAI_API_KEY=your-key-here" > .env

# 4. Run interactive session
python main.py

# Example session:
# 📂 Knowledge Base loaded (8 files):
#  [1] primary/brand-guidelines.md        (MD)     1.2 KB
#  [2] primary/bank-statements.pdf        (PDF)    0.8 KB
#  ...
#
# > remove 2
# ✓ Removed: primary/bank-statements.pdf (7 files loaded)
#
# > add ~/research/new_trends.md
# ✓ Added: new_trends.md (MD) (8 files loaded)
#
# > add ~/interviews/genz_talk.mp3
# ⏳ Transcribing audio via Whisper API...
# ✓ Added: genz_talk.mp3 (AUDIO → transcribed) (9 files loaded)
#
# > add https://www.youtube.com/watch?v=abc123
# ⏳ Fetching YouTube transcript...
# ✓ Added: youtube_abc123 (YOUTUBE) (10 files loaded)
#
# > list
# 📂 Knowledge Base (10 files):
#  [1] primary/brand-guidelines.md        (MD)      1.2 KB
#  ...
#
# > prompt
# 📝 Current system prompt (from prompts/system_prompt.md):
# ─────────────────────────────────
# You are LazyInvest, a financial coach for Gen Z...
# ─────────────────────────────────
#
# > prompt edit
# ✏️  Opening system prompt in editor...
# ✓ System prompt updated and reloaded.
#
# > prompt reset
# ✓ System prompt restored to default.
#
# > generate --topic "first paycheck" --style educational
# 🐦 Generated Tweet:
# "You just got your first paycheck and it's already gone?..."
#
# > quit
```

---

## 10. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| LLM ignores brand voice | Strong system prompt + include content examples in context |
| Tweets exceed 280 chars | Post-processing validation + retry with "make it shorter" |
| Generic-sounding output | Include competitor examples as "what NOT to sound like" |
| Knowledge base too large for context | Selective loading based on topic relevance |
| API rate limits | Simple retry with backoff; batch generation with delays |

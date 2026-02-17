MoneySavvy AI – Gen Z Financial Coach Content Engine

MoneySavvy AI is an AI Content Creator system designed to generate relatable, educational, and non-generic financial content for Gen Z.

The system serves as the main interface between our company and young adults starting their financial journey by producing brand-aligned financial education content as daily tweets on X (Twitter).

Our goal is to build trust through education and guide users toward healthier financial habits — from their first paycheck to their first investments.

🎯 Project Goals

MoneySavvy AI aims to:

Build a strong and consistent brand identity

Educate Gen Z about budgeting, spending, saving, and investing

Make financial topics simple, relatable, and practical

Support financial health from the first income onward

Convert education into trust and long-term engagement

The system avoids generic AI content by grounding outputs in real-life Gen Z scenarios and structured financial knowledge.

👥 Target Audience

Gen Z (17–23 years old, Europe-based)
Young adults managing their first income and financial independence.

Typical situations referenced in content:

- First rent or shared apartment (WG)
- Subscriptions (Spotify, Netflix, gym, delivery apps)
- Eating out, clubbing, lifestyle spending
- Saving for travel, car, or laptop
- Curiosity about ETFs and first investments

🚀 MVP Scope

The MVP focuses on generating three educational tweets per day on X around a specific life topic (e.g., holidays, clubbing, subscriptions), always connected to smart financial decision-making.

The system:

Uses a brand-specific tone of voice

Injects real Gen Z scenarios and financial pain points

Grounds content in economic context and behavioral insights

Demonstrates clear differentiation from generic AI outputs

Education → Trust → Referral

🧠 Knowledge Base Architecture

The content engine is powered by two structured knowledge bases.

Primary Knowledge Base (Company-Specific)

Focused on brand voice and real Gen Z behavior:

brand_guidelines.md – brand tone and communication style

genz_combined_pain_points.md – key financial struggles

genz_statements_summaries.md – simulated bank statements and user behavior insights

Secondary Knowledge Base (Industry & Context)

Focused on financial education and market realities:

economic_situation_summary.md – general economic context

transcriptoftheeuropeangenZs.md – interview transcript insights

common_money_traps.md – subscriptions, BNPL, impulse spending

competitor_analysis.md – market positioning

genz_patterns.md – behavioral trends

investing_basics.md – ETF and long-term investing fundamentals

Gen Z Financial Tweet Examples.md – reference content patterns

🔁 Content Generation Pipeline (MVP)

Ingest markdown documents from both knowledge bases

Structure and curate relevant context

Apply prompt templates aligned with brand voice

Generate daily educational tweets

Save outputs for review and comparison

🧪 Demonstrating Uniqueness

To avoid generic AI content, the project includes:

Side-by-side comparisons between generic ChatGPT prompts and MoneySavvy AI outputs

Context injection from real Gen Z scenarios and financial research

Brand tone enforcement through prompt templates

Uniqueness examples are documented in:

uniqueness_report.md
🛠️ Tech Stack

Python 3.8+

OpenAI GPT-5 Mini API

Markdown document processing

VS Code development environment

GitHub version control

📂 Project Structure
ai-content-creator/
├── src/
│   ├── document_processor.py
│   ├── knowledge_base.py
│   ├── prompt_templates.py
│   ├── content_pipeline.py
│   ├── llm_integration.py
│   └── main.py
├── knowledge_base/
│   ├── primary/
│   └── secondary/
├── templates/
├── config/
│   └── vscode_agent.json
├── outputs/
├── requirements.txt
├── .env.example
├── README.md
└── uniqueness_report.md
⚙️ Setup Instructions
1. Clone the repository
git clone <repository-url>
cd ai-content-creator
2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
3. Install dependencies
pip install -r requirements.txt
4. Configure API key

Create a .env file:

OPENAI_API_KEY=your_api_key_here
▶️ Run the Content Generator
python src/main.py

Generated tweets will appear in the outputs/ folder.

👨‍👩‍👧‍👦 Team

Javier Romero

Anson Knausenberger

Kathrin Sühlsen

Artem Pereyaslavtsev

Szilard Pap

📈 Key Learning Outcomes

Structured content generation using knowledge bases

Advanced prompt engineering for brand alignment

Avoiding generic AI outputs through contextual grounding

Building automated content workflows

Demonstrating real-world AI content differentiation

# MoneySavy AI — Cost Analysis Report

> **API-powered content generation vs ChatGPT Plus & Pro subscriptions**
>
> Date: February 2026 | Model: GPT-5.2

---

## 1. Token Usage Per Request

Every call to `generate_daily_content` sends the following payload:

| Component               | Characters | Est. Tokens |
| ----------------------- | ---------- | ----------- |
| System prompt           | ~3,875     | ~970        |
| Knowledge Base (all KB) | ~68,969    | ~17,240     |
| Brand guidelines        | ~7,218     | ~1,805      |
| User message (topic)    | ~150       | ~40         |
| **Total input**         | **~80,212** | **~20,055** |

> Token estimation: ~1 token per 4 characters (English text with markdown).

**Output tokens** (3 tweets + formatting): ~200–400 tokens per request.

If a tweet exceeds 280 chars and triggers a **retry**, the conversation grows by ~200 tokens (assistant reply + correction prompt), but this is rare for `generate_daily_content`.

---

## 2. GPT-5.2 API Pricing

| Metric         | Rate                          |
| -------------- | ----------------------------- |
| Input tokens   | **$1.75 / 1M tokens**        |
| Output tokens  | **$14.00 / 1M tokens**       |
| Cached input   | **$0.175 / 1M tokens** (90% discount for repeated system prompts) |

---

## 3. Cost Per Request

### Without caching

| Token type | Tokens  | Cost                        |
| ---------- | ------- | --------------------------- |
| Input      | 20,055  | 20,055 / 1M x $1.75 = **$0.0351** |
| Output     | 350     | 350 / 1M x $14.00 = **$0.0049** |
| **Total**  |         | **~$0.040 per request**     |

### With prompt caching (steady state)

Once the system prompt + KB context are cached (after the first request), subsequent requests benefit from the 90% discount on repeated input tokens. Roughly ~20,000 of the 20,055 input tokens are cacheable.

| Token type     | Tokens  | Cost                              |
| -------------- | ------- | --------------------------------- |
| Cached input   | 20,000  | 20,000 / 1M x $0.175 = **$0.0035** |
| Uncached input | 55      | 55 / 1M x $1.75 = **$0.0001**    |
| Output         | 350     | 350 / 1M x $14.00 = **$0.0049** |
| **Total**      |         | **~$0.0085 per request**          |

---

## 4. Monthly Usage Scenarios

The app generates **3 tweets/day, 7 days/week** = **~90 requests/month** (one request per day generates all 3 tweets). Realistically, accounting for testing, iteration, and reruns:

| Scenario                        | Requests/month | Cost (no cache) | Cost (cached) |
| ------------------------------- | -------------- | --------------- | ------------- |
| Production only (1x/day)        | 30             | $1.20           | $0.26         |
| Production + testing (2x/day)   | 60             | $2.40           | $0.51         |
| Active development (5x/day)     | 150            | $6.00           | $1.28         |
| Heavy usage (10x/day)           | 300            | $12.00          | $2.55         |

---

## 5. Comparison: API vs ChatGPT Plus vs ChatGPT Pro

| Criteria                     | MoneySavy AI (API)               | ChatGPT Plus                      | ChatGPT Pro                        |
| ---------------------------- | -------------------------------- | --------------------------------- | ---------------------------------- |
| **Monthly cost**             | **$0.26 – $12.00**              | **$20/month (fixed)**             | **$200/month (fixed)**             |
| **Model access**             | GPT-5.2                          | GPT-5.2 Thinking + legacy models  | GPT-5.2 Pro + all models           |
| **Automation**               | Fully automated, scriptable      | Manual copy-paste                  | Manual copy-paste                  |
| **Consistency**              | Same prompt every time            | Depends on user input              | Depends on user input              |
| **Knowledge base**           | Custom KB injected automatically  | Must paste context manually        | Must paste context manually        |
| **Brand voice**              | Enforced by system prompt         | Must remind ChatGPT each time      | Must remind ChatGPT each time      |
| **Scalability**              | Unlimited (pay per use)          | Message limits apply               | Higher limits, but still manual    |
| **Context window**           | Full 400K (API control)          | Limited by chat UI                 | Maximum memory and context         |
| **Extra features**           | Only what you build               | Codex, file uploads, memory        | All Plus features + early previews |
| **Annual cost (production)** | **~$3 – $144/year**             | **$240/year**                      | **$2,400/year**                    |

### Break-even analysis

**vs ChatGPT Plus ($20/month):**

- **Without caching:** $20 / $0.040 = **500 requests/month** (~17/day)
- **With caching:** $20 / $0.0085 = **2,353 requests/month** (~78/day)

**vs ChatGPT Pro ($200/month):**

- **Without caching:** $200 / $0.040 = **5,000 requests/month** (~167/day)
- **With caching:** $200 / $0.0085 = **23,529 requests/month** (~784/day)

Even compared to the much cheaper Plus plan, the app would need **17–78 requests/day** to break even — far beyond the ~1 request/day needed in production.

---

## 6. Key Takeaways

1. **The API is 1.7x–77x cheaper than ChatGPT Plus** and **16x–770x cheaper than ChatGPT Pro** for this use case, depending on caching and volume.

2. **At production volume (30 req/month with caching), the app costs ~$0.26/month** — 1.3% of Plus and 0.13% of Pro.

3. **Caching reduces costs by ~79%** since the system prompt and KB context are identical across requests.

4. **ChatGPT Plus ($20/mo)** is the most tempting alternative — but even at that price, the API is still **77x cheaper** with caching at production volume. Plus also introduces manual effort, inconsistent prompting, and message limits that make it impractical for daily automated content generation.

5. **ChatGPT Pro ($200/mo)** only makes sense if you need interactive access to the most powerful model across many different tasks. For a **single, automated, repeatable task** like content generation, it's dramatically overpriced.

6. **Total annual cost comparison:**

   | Plan              | Annual Cost |
   | ----------------- | ----------- |
   | API (cached, prod) | **~$3**    |
   | API (no cache, heavy) | **~$144** |
   | ChatGPT Plus      | **$240**    |
   | ChatGPT Pro       | **$2,400**  |

---

## Sources

- [OpenAI API Pricing](https://openai.com/api/pricing/)
- [GPT-5.2 API Pricing Details](https://pricepertoken.com/pricing-page/model/openai-gpt-5.2)
- [ChatGPT Plus Plan](https://chatgpt.com/plans/plus/)
- [ChatGPT Pro Plan](https://chatgpt.com/plans/pro/)
- [ChatGPT Plans Comparison](https://intuitionlabs.ai/articles/chatgpt-plans-comparison)

# 🏗️ RAG Article App — Architecture & Workflow

> End-to-end architecture for an AI-powered article search and summarization app using CrewAI Flow, Firebase, BigQuery, and Vertex AI.

---

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT (Mobile Web)                  │
└─────────────────────────┬───────────────────────────────────┘
                          │  POST /api/v1/search
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Cloud Run — FastAPI + CrewAI Flow              │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  ArticleFlow                        │   │
│   │                                                     │   │
│   │  @start → check_bigquery_cache                      │   │
│   │      ↓                                              │   │
│   │  @router → route_after_cache                        │   │ 
│   │      ↙               ↘                              │   │
│   │  cache_hit         cache_miss                       │   │
│   │      ↓                 ↓                            │   │
│   │  return_result    fetch_from_web (Agent)            │   │
│   │                       ↓                             │   │
│   │                  summarize (Agent)                  │   │
│   │                       ↓                             │   │
│   │                  generate_embedding                 │   │
│   │                       ↓                             │   │
│   │                  save_to_firebase                   │   │
│   │                       ↓                             │   │
│   │                  save_to_bigquery                   │   │
│   │                       ↓                             │   │
│   │                  return_result                      │   │
│   └─────────────────────────────────────────────────────┘   │
└──────────┬──────────────────────┬───────────────────────────┘
           │                      │
           ▼                      ▼
┌─────────────────┐    ┌─────────────────────────────────────┐
│    Firebase     │    │              BigQuery               │
│   (Firestore)   │    │                                     │
│                 │    │  articles table:                    │
│ - title         │    │  - title, summary, url              │
│ - summary       │    │  - full_content                     │
│ - url           │    │  - embedding (vector)               │
│ - thumbnail     │    │  - fetched_at                       │
│ - published_at  │    │                                     │
│                 │    │  VECTOR_SEARCH() for RAG            │
│ Used for:       │    │  Used for:                          │
│ Feed/Browse UI  │    │  Semantic Search + RAG              │
└─────────────────┘    └─────────────────────────────────────┘
```

---

## 🔄 Detailed Flow — User Search

```
User types query in app
          │
          ▼
POST /api/v1/search {"query": "AI trends 2026"}
          │
          ▼
┌─────────────────────────────┐
│  ArticleFlow.kickoff_async  │
│  inputs: {query: "..."}     │
│  → maps to ArticleState     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  @start                     │
│  check_bigquery_cache()     │
│                             │
│  VECTOR_SEARCH() in BQ      │
│  with query embedding       │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  @router                    │
│  route_after_cache()        │
└────────┬──────────┬─────────┘
         │          │
    cache_hit    cache_miss
         │          │
         ▼          ▼
┌──────────┐  ┌─────────────────────────┐
│ return   │  │  @listen("cache_miss")  │
│ articles │  │  fetch_from_web()       │
│ from BQ  │  │                         │
└──────────┘  │  Web Search Agent       │
              │  → SerperDev Tool       │
              │  → Scrape Article       │
              └───────────┬─────────────┘
                          │
                          ▼
              ┌─────────────────────────┐
              │  @listen(fetch_from_web)│
              │  summarize_article()    │
              │                         │
              │  Summary Agent          │
              │  → OpenAI LLM           │
              │  → Generate summary     │
              └───────────┬─────────────┘
                          │
                          ▼
              ┌─────────────────────────┐
              │  @listen(summarize)     │
              │  generate_embedding()   │
              │                         │
              │  Vertex AI              │
              │  text-embedding-005     │
              │  → vector [0.1, 0.2...] │
              └───────────┬─────────────┘
                          │
                          ▼
              ┌─────────────────────────┐
              │  @listen(embedding)     │
              │  save_data()            │
              │                         │
              │  → Firebase (summary)   │
              │  → BigQuery (full+emb)  │
              └───────────┬─────────────┘
                          │
                          ▼
              ┌─────────────────────────┐
              │  @listen(save_data)     │
              │  return_result()        │
              │  → return to user       │
              └─────────────────────────┘
```

---

## 📰 User Browse Flow (No Search)

```
User opens app
      │
      ▼
GET /api/v1/articles
      │
      ▼
Read directly from Firebase (Firestore)
      │
      ▼
Return [title, summary, thumbnail, url, published_at]
      │
      ▼
Display article feed in UI
```

> [InBits] (https://www.inbits.co/) 
<br/>
> [GitHub Repo] (https://github.com/amitvermaknw/inbits)

---

## 🤖 CrewAI Agents

### Web Search Agent
```
Role    : Web Research Specialist
Tools   : SerperDevTool, ScrapeWebsiteTool
Goal    : Find and extract full article content from the web
Trigger : cache_miss in flow
```

### Summary Agent
```
Role    : Article Summarizer
LLM     : OpenAI
Goal    : Generate concise, readable article summary
Trigger : After web search agent completes
```

---

## 🗄️ Data Schema

### Firebase (Firestore) — `articles` collection
| Field | Type | Purpose |
|---|---|---|
| `id` | string | URL hash |
| `title` | string | Article title |
| `summary` | string | AI generated summary |
| `url` | string | Source URL |
| `thumbnail` | string | Image URL |
| `published_at` | timestamp | Publish date |
| `source` | string | web_search / manual |

### BigQuery — `articles` table
| Field | Type | Purpose |
|---|---|---|
| `id` | STRING | URL hash (matches Firebase) |
| `title` | STRING | Article title |
| `summary` | STRING | AI generated summary |
| `url` | STRING | Source URL |
| `full_content` | STRING | Complete article text |
| `embedding` | ARRAY<FLOAT64> | Vector for semantic search |
| `fetched_at` | TIMESTAMP | When fetched |
| `source` | STRING | Origin of article |

---

## 💰 Cost Estimate (POC)

| Service | Usage | Cost |
|---|---|---|
| Cloud Run | Low traffic POC | ~$0 (free tier) |
| Firebase Firestore | Lightweight docs | ~$0 (free tier) |
| BigQuery Storage | 100MB | ~$0 (free tier 10GB) |
| BigQuery Queries | < 1TB/month | ~$0 (free tier) |
| Vertex AI Embeddings | Per 1K chars | ~$0.0001 |
| **Total POC** | | **~$0–2/month** |

> ⚠️ Vertex AI Vector Search NOT used — BigQuery VECTOR_SEARCH() used instead for POC cost savings. Migrate to Vertex AI Vector Search only when production low-latency (<50ms) is needed.

---

## 🚀 Deployment

```bash
# Build and deploy to Cloud Run
gcloud run deploy article-rag-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=your-project-id
```

---

## 🔮 Future: Production Migration

```
POC (Now)                    Production (Later)
─────────────────────        ──────────────────────────
BigQuery VECTOR_SEARCH()  →  Vertex AI Vector Search
Single Cloud Run instance →  Cloud Run autoscaling
Manual embedding batch    →  Eventarc trigger on new doc
```
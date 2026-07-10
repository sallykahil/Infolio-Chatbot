# Infolio — RAG Chatbot for Small Businesses

Multi-tenant RAG bot. Each business gets their own isolated knowledge base.
Upload PDFs or a website URL → customers ask questions → answers come from YOUR data only.

**Live**: [API](https://web-production-9963e.up.railway.app) · [Dashboard](https://web-production-9963e.up.railway.app/dashboard)

## Stack
- **Backend**: FastAPI + LangChain + Qdrant + Groq (Llama 3)
- **Embeddings**: HuggingFace all-MiniLM-L6-v2 (free, runs locally)
- **Frontend**: `dashboard.html` — plain HTML/CSS/JS, served by FastAPI via `GET /dashboard`
- **Hosting**: Railway, single service, auto-deploys from GitHub `main`
- **Vector DB**: Qdrant Cloud

## Local Development

Get free API keys from [Groq](https://console.groq.com) and [Qdrant Cloud](https://cloud.qdrant.io).
For Qdrant, use a **Database API key** with Manage access on the cluster — a
collection-restricted key can't list/create/delete collections.

Create a `.env` file (gitignored) in the project root:
```bash
GROQ_API_KEY=your-groq-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-key
EMBED_MODEL=all-MiniLM-L6-v2
TOP_K=3
```

Install and run:
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
API docs: http://localhost:8000/docs · Dashboard: http://localhost:8000/dashboard

## Deploying to Railway

Push to `main` and Railway auto-builds and redeploys. Set the same env vars
above in Railway → your service → **Variables** — Railway doesn't read your
local `.env`. A deploy usually takes 1–3 minutes; once **Active**, the
service stays running continuously.

## How to Use

Enter a Business ID (e.g. `sallycrochet`) — one per client — then upload
their PDFs or paste a website URL to index it. Use **Test Bot** to verify
answers, then **Embed** to copy the widget snippet onto their site. Delete a
business card to remove a tenant and its indexed data.

## API Endpoints

| Method | Endpoint | What it does |
|--------|----------|-------------|
| GET  | `/dashboard` | Serves the dashboard UI |
| GET  | `/widget.js` | Embeddable chat widget script |
| POST | `/upload-docs?tenant_id=X` | Upload PDF files |
| POST | `/ingest-url` | Scrape and index a URL |
| POST | `/ask` | Ask a question |
| GET  | `/tenants` | List all businesses |
| DELETE | `/tenants/{tenant_id}` | Delete a business and its indexed data |

## Pricing Tiers (for your clients)
- **Free**: 50 queries/month — good for demos
- **Pro $29/mo**: 2,000 queries, 10 PDFs
- **Business $79/mo**: Unlimited queries, unlimited docs, widget customization

## Roadmap
Stripe subscriptions, per-tenant auth, and an ASP.NET wrapper around the dashboard.

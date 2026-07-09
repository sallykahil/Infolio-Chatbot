# Infolio — RAG Chatbot for Small Businesses

Multi-tenant RAG bot. Each business gets their own isolated knowledge base.
Upload PDFs or a website URL → customers ask questions → answers come from YOUR data only.

---

## Live URLs

- **API**: https://web-production-9963e.up.railway.app
- **Dashboard**: https://web-production-9963e.up.railway.app/dashboard

Both are served by the same Railway service — pushing to `main` redeploys them together.

---

## Stack
- **Backend**: FastAPI + LangChain + Qdrant + Groq (Llama 3)
- **Embeddings**: HuggingFace all-MiniLM-L6-v2 (free, runs locally)
- **Frontend**: `dashboard.html` — plain HTML/CSS/JS, served by FastAPI via `GET /dashboard`
- **Hosting**: Railway (single service, auto-deploys from GitHub `main`)
- **Vector DB**: Qdrant Cloud

---

## Local Development

### 1. Get your free API keys
- **Groq** (LLM): https://console.groq.com → free, fast Llama 3
- **Qdrant Cloud** (vector DB): https://cloud.qdrant.io → free 1GB cluster
  - Use a **Database API key** with Manage access for the cluster (not a
    collection-restricted key — it needs to list/create/delete collections).

### 2. Set environment variables
Create a `.env` file (gitignored) in the project root:
```bash
GROQ_API_KEY=your-groq-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-key
EMBED_MODEL=all-MiniLM-L6-v2
TOP_K=3
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the API
```bash
uvicorn main:app --reload --port 8000
```
API docs at: http://localhost:8000/docs
Dashboard at: http://localhost:8000/dashboard

---

## Deploying to Railway

1. Push to `main` on GitHub — Railway auto-builds and redeploys the connected service.
2. In Railway → your service → **Variables**, set the same env vars as above
   (`GROQ_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `EMBED_MODEL`, `TOP_K`).
   Railway does not read your local `.env` — these must be set in the dashboard.
3. Deploys typically take 1–3 minutes. Once **Active**, the service stays running continuously.

---

## How to Use

1. Enter a **Business ID** (e.g. `sallycrochet`) — one per client
2. Upload their PDFs (catalog, FAQ, price list, menu…)
3. Or paste their website URL
4. Go to **Test Bot** → ask questions → verify it works
5. Go to **Embed** → copy the JS snippet → paste on their site
6. Use **Delete** on a business card to remove a tenant and its indexed data

---

## API Endpoints

| Method | Endpoint | What it does |
|--------|----------|-------------|
| GET  | `/dashboard` | Serves the dashboard UI |
| POST | `/upload-docs?tenant_id=X` | Upload PDF files |
| POST | `/ingest-url` | Scrape and index a URL |
| POST | `/ask` | Ask a question |
| GET  | `/tenants` | List all businesses |
| DELETE | `/tenants/{tenant_id}` | Delete a business and its indexed data |

---

## Pricing Tiers (for your clients)
- **Free**: 50 queries/month — good for demos
- **Pro $29/mo**: 2,000 queries, 10 PDFs
- **Business $79/mo**: Unlimited queries, unlimited docs, widget customization

---

## Next Steps
- [ ] Add Stripe for subscriptions
- [ ] Add auth (JWT per tenant)
- [ ] Build widget.js (embeddable chat bubble)
- [ ] Build ASP.NET wrapper around the dashboard

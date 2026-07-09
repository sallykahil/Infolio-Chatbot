# Infolio — RAG Chatbot for Small Businesses

Multi-tenant RAG bot. Each business gets their own isolated knowledge base.
Upload PDFs or a website URL → customers ask questions → answers come from YOUR data only.

---

## Stack
- **Backend**: FastAPI + LangChain + Qdrant + Groq (Llama 3)
- **Embeddings**: HuggingFace all-MiniLM-L6-v2 (free, runs locally)
- **Frontend**: HTML/CSS/JS dashboard (plug into ASP.NET easily)

---

## Setup in 5 Steps

### 1. Get your free API keys
- **Groq** (LLM): https://console.groq.com → free, fast Llama 3
- **Qdrant Cloud** (vector DB): https://cloud.qdrant.io → free 1GB cluster

### 2. Set environment variables
```bash
export GROQ_API_KEY="your-groq-key"
export QDRANT_URL="https://your-cluster.qdrant.io"
export QDRANT_API_KEY="your-qdrant-key"
```

### 3. Install dependencies
```bash
cd api
pip install -r requirements.txt
```

### 4. Run the API
```bash
uvicorn main:app --reload --port 8000
```
API docs at: http://localhost:8000/docs

### 5. Open the dashboard
Open `frontend/dashboard.html` in your browser (or serve via ASP.NET).

---

## How to Use

1. Enter a **Business ID** (e.g. `sallycrochet`) — one per client
2. Upload their PDFs (catalog, FAQ, price list, menu…)
3. Or paste their website URL
4. Go to **Test Bot** → ask questions → verify it works
5. Go to **Embed** → copy the JS snippet → paste on their site

---

## API Endpoints

| Method | Endpoint | What it does |
|--------|----------|-------------|
| POST | `/upload-docs?tenant_id=X` | Upload PDF files |
| POST | `/ingest-url` | Scrape and index a URL |
| POST | `/ask` | Ask a question |
| GET  | `/tenants` | List all businesses |
| Delete  | `/tenants` | delete chosen business|


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
- [ ] Deploy API to Railway/Render
- [ ] Build ASP.NET wrapper around the dashboard

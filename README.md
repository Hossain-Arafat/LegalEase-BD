Here's the complete documentation for LegalEase BD application:

---

# LegalEase BD - AI Legal Assistant for Bangladeshi Law

[![Modal](https://img.shields.io/badge/Modal-Cloud-blue)](https://modal.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA--3--70B-orange)](https://groq.com)
[![Python](https://img.shields.io/badge/Python-3.11-green)](https://python.org)

## 📋 Overview

LegalEase BD is an AI-powered legal assistant specifically designed for Bangladeshi law. It combines **hybrid search** (semantic + keyword) with **LLM generation** to provide accurate, cited legal answers in both English and Bengali.

### Key Features

- ✅ **Bilingual Support** - Answers questions in English or Bengali
- ✅ **Hybrid Search** - Combines ChromaDB (semantic) + BM25 (keyword)
- ✅ **35K Legal Chunks** - Comprehensive coverage of Bangladeshi acts
- ✅ **LLaMA-3-70B** - Powered by Groq's ultra-fast free tier
- ✅ **Production Ready** - Deployed on Modal with auto-scaling
- ✅ **Low Cost** - Free tier (Groq) + $30 Modal credit

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER FRONTEND                               │
│                    (HTML/React/Mobile App)                          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FASTAPI GATEWAY (Modal)                          │
│  Endpoint: /query                                                   │
│  - Receives user questions                                          │
│  - Routes to LLM service                                            │
│  - Returns formatted responses                                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LLM SERVICE (Modal - GPU T4)                     │
│  - Hybrid Search (ChromaDB + BM25)                                  │
│  - Language detection (English/Bengali)                             │
│  - Query expansion & translation                                    │
│  - Citation extraction                                              │
└─────────────────────────────────────────────────────────────────────┘
                           │                    │
            ┌──────────────┘                    └──────────────┐
            ▼                                                  ▼
┌────────────────────────────┐                        ┌───────────────────────┐
│   CHROMADB (35K vectors)   │                        │   BM25 (35K chunks)   │
│   - Semantic search        │                        │   - Keyword search    │
│   - Multilingual embeddings│                        │   - Legal stopwords   │
└────────────────────────────┘                        └───────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    GROQ API (LLaMA-3-70B)                           │
│  - Generates natural language answers                               │
│  - Follows strict legal formatting                                  │
│  - FREE tier (30 requests/minute)                                   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FINAL RESPONSE                               │
│  📘 EXPLANATION - Plain language answer                             │
│  ⚖️ LEGAL BASIS - Act name & section                                │
│  🪜 NEXT STEPS - Concrete actions                                   │
│  ⚠️ WARNING - Legal caveats                                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
legalease/
│
├── README.md
│
├── frontend/
│   ├── public/
│   │   ├── favicon.svg
│   │   └── icons.svg
│   │
│   ├── src/
│   │   ├── assets/
│   │   │   ├── hero.png
│   │   │   ├── react.svg
│   │   │   └── vite.svg
│   │   │
│   │   ├── components/
│   │   │   └── Chatbot.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Chat.jsx
│   │   │   └── Home.jsx
│   │   │
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── .gitignore
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vercel.json
│   ├── vite.config.js
│   └── README.md
│
├── legalease_modal/
│   ├── data/
│   │   ├── chunks/
│   │   │   ├── acts_bengali.json #not uploaded for size constraints
│   │   │   └── acts_english.json #not uploaded for size constraints
│   │   │
│   │   └── indexes/ #scripts for building indexes are given
│   │
│   ├── scripts/
│   │   ├── build_full_chromadb.py #scripts for building chromaDB index
│   │   ├── build_indexes.py #Fixes dictionary format
│   │   ├── rebuild_bm25.py #Building BM25 index
│   │   ├── rebuild_local.py
│   │   └── legalease_modal.py 
│   │
│   ├── modal_fastapi.py
│   ├── modal_llm.py
│   ├── prompt.md #some prompts across all domain to test the model
│   ├── requirements.txt
│   └── README.md #this file
│
└── .gitignore
```

---

## 🚀 Deployment Guide

### Prerequisites

```bash
# Python 3.11 required
python --version  # Should show 3.11.x

# Install Modal CLI
pip install modal

# Authenticate with Modal
modal token set
```

### Step 1: Prepare Your Data

```bash
# Place your JSON files in data/chunks/
data/chunks/
├── Acts_english.json
└── Acts_bengali.json
```

### Step 2: Build Search Indexes (Local)

```python
# rebuild_chromadb.py - Creates vector database
python rebuild_chromadb.py

# rebuild_bm25.py - Creates keyword index  
python rebuild_bm25.py
```

### Step 3: Upload to Modal

```bash
# Upload indexes to Modal volume
python -m modal volume put --force legalease-data data/indexes /indexes
python -m modal volume put --force legalease-data data/chunks /chunks
```

### Step 4: Deploy Services

```bash
# Deploy LLM service first
python -m modal deploy modal_llm.py

# Deploy FastAPI gateway
python -m modal deploy modal_fastapi.py
```

### Step 5: Test Your API

```bash
# English query
curl -X POST https://your-modal-endpoint.modal.run/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the punishment for murder?"}'

# Bengali query  
curl -X POST https://your-modal-endpoint.modal.run/query \
  -H "Content-Type: application/json" \
  -d '{"query": "বাংলাদেশে হত্যার শাস্তি কী?"}'
```

---

## 📊 API Documentation

### Endpoint

```
POST https://your-modal-endpoint.modal.run/query
```

### Request Format

```json
{
    "query": "Your legal question here",
    "top_k": 5  // Optional, number of sources to retrieve
}
```

### Response Format

```json
{
    "query": "What is the punishment for murder?",
    "language": "en",
    "response": "📘 EXPLANATION: ...\n⚖️ LEGAL BASIS: ...\n🪜 NEXT STEPS: ...\n⚠️ WARNING: ...",
    "citations": [
        {
            "act": "The Penal Code, 1860",
            "act_no": "XLV",
            "year": "1860",
            "section": "Section 302"
        }
    ],
    "confidence": "HIGH",
    "sources_count": 3,
    "processing_time_ms": 1012
}
```

### Response Fields

| Field | Description |
|-------|-------------|
| `query` | Original user question |
| `language` | Detected language (en/bn) |
| `response` | AI-generated legal answer |
| `citations` | Legal sources used |
| `confidence` | HIGH/MEDIUM/LOW |
| `sources_count` | Number of retrieved sources |
| `processing_time_ms` | Response time in milliseconds |

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key (get from console.groq.com) | Yes |

### Modal Settings

GPU-enabled deployment

---

## 💰 Cost Breakdown

Uses Groq free tier and Modal credits for low-cost deployment.

---

## 🧪 Testing Examples

### English Queries

```bash
# Criminal law
"What is the punishment for robbery in Bangladesh?"

# Family law  
"How can a Muslim woman get divorce?"

# Property law
"What is the land registration process?"

# Constitutional law
"What are fundamental rights?"
```

### Bengali Queries

```bash
# Criminal law
"বাংলাদেশে ডাকাতির শাস্তি কী?"

# Family law
"মুসলিম নারী কীভাবে তালাক নিতে পারেন?"

# Property law
"জমি নিবন্ধন প্রক্রিয়া কেমন?"
```

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| **Cold start** | 30-60 seconds |
| **Subsequent requests** | 1-2 seconds |
| **Concurrent requests** | Up to 10 |
| **Vector database size** | 35,472 chunks |
| **Supported languages** | English, Bengali |

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **Module not found** | `pip install -r requirements.txt` |
| **Modal authentication failed** | `modal token set` |
| **ChromaDB has 0 vectors** | Rebuild indexes with `rebuild_chromadb.py` |
| **Groq API error** | Check API key at console.groq.com |
| **Slow responses** | First request is cold start; subsequent are fast |

### Checking Health

```bash
# Check if API is running
curl https://your-modal-endpoint.modal.run/health

# Check Modal logs
modal logs legalease-llm

# Check volume contents
python -m modal volume ls legalease-data
```

---

## 🔒 Security Considerations

- ✅ API has CORS enabled for frontend access
- ✅ Groq API key stored as environment variable
- ✅ No sensitive data stored in code
- ✅ Modal volumes encrypted at rest

---

## 📝 Future Improvements

- [ ] Add more legal acts and sections
- [ ] Implement user authentication
- [ ] Add rate limiting
- [ ] Cache frequent queries
- [ ] Add streaming responses
- [ ] Support PDF upload for custom documents

---

## 👥 Contributors

- Built for LegalEase BD project
- Architecture: Hybrid RAG (Retrieval-Augmented Generation)
- Deployment: Modal (serverless GPU) + Groq (LLM)

---

## 📄 License

This project is proprietary and confidential.

---

## 🆘 Support

For issues or questions:
- Check Modal logs: `modal logs legalease-llm`
- Check FastAPI status: `https://your-modal-endpoint.modal.run/health`

---

## 🎯 Quick Start Commands

```bash
# 1. Install dependencies
pip install modal chromadb sentence-transformers rank-bm25

# 2. Build indexes
python rebuild_chromadb.py
python rebuild_bm25.py

# 3. Upload to Modal
python -m modal volume put --force legalease-data data/indexes /indexes

# 4. Deploy
python -m modal deploy modal_llm.py
python -m modal deploy modal_fastapi.py

# 5. Test
curl -X POST https://your-modal-endpoint.modal.run/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the punishment for murder?"}'
```

---

## ✅ Success Criteria

- [x] API responds to POST requests
- [x] Returns structured legal answers
- [x] Citations included
- [x] Bengali language support
- [x] Fast responses (1-2 seconds after warmup)
- [x] Production deployment on Modal
- [x] Free tier LLM (Groq)

---

**LegalEase BD is ready for deployment! 🚀**

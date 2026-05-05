# modal_fastapi.py - Production Ready with CORS Restriction
import modal
from modal import App, Image, asgi_app

app = modal.App("legalease-api")

GROQ_API_KEY = "PLACEHOLDER_FOR_GROQ_API_KEY"  # Set this in Modal secrets for production

api_image = Image.debian_slim().pip_install(
    "fastapi",
    "uvicorn", 
    "pydantic",
    "httpx",
)

llm_class = modal.Cls.from_name("legalease-llm", "LegalEaseLLM")
llm_instance = llm_class()
search_method = llm_instance.search

# Allowed frontend URLs (hardcoded for production)
ALLOWED_ORIGINS = [
    "set your production frontend URL here",  # e.g. https://legaleasebd.com
    "set your local development URL here",  # For local React development
]

@app.function(image=api_image)
@asgi_app()
def fastapi_app():
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from typing import List, Optional
    import httpx
    import time
    
    web_app = FastAPI(
        title="LegalEase BD API",
        description="Bangladeshi Legal Assistant with RAG",
        version="3.0.0"
    )
    
    # CORS - Only allow specific frontend
    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["POST", "GET", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type"],
        max_age=3600,
    )
    
    class QueryRequest(BaseModel):
        query: str
        top_k: int = 5
    
    class Citation(BaseModel):
        act: str
        act_no: str
        year: str
        section: str
    
    class QueryResponse(BaseModel):
        query: str
        language: str
        response: str
        citations: List[Citation]
        confidence: str
        sources_count: int
        processing_time_ms: float
    
    @web_app.get("/")
    async def root():
        return {
            "service": "LegalEase BD",
            "version": "3.0.0",
            "status": "running",
            "allowed_origins": ALLOWED_ORIGINS,
            "endpoints": {
                "POST /query": "Ask a legal question",
                "GET /health": "Health check"
            }
        }
    
    @web_app.get("/health")
    async def health():
        groq_ok = False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": "Test"}],
                        "max_tokens": 5
                    },
                    timeout=10.0
                )
                groq_ok = response.status_code == 200
        except Exception as e:
            print(f"Groq health check error: {e}")
        
        modal_ok = False
        try:
            health_result = await search_method.remote.aio("test", 1, False)
            modal_ok = health_result.get("status") == "success"
        except Exception as e:
            print(f"Modal health check error: {e}")
        
        return {
            "status": "healthy",
            "groq_connected": groq_ok,
            "modal_connected": modal_ok,
            "allowed_origins": ALLOWED_ORIGINS
        }
    
    @web_app.post("/query", response_model=QueryResponse)
    async def query_endpoint(request: QueryRequest):
        """Process a legal question and return AI-generated answer"""
        start_time = time.time()
        
        # Step 1: Retrieve relevant legal chunks from Modal LLM service
        print(f"📚 Retrieving for: {request.query[:50]}...")
        results = await search_method.remote.aio(request.query, request.top_k, False)
        
        # Step 2: Check if we have results
        if not results.get("sources"):
            return QueryResponse(
                query=request.query,
                language=results.get("language", "en"),
                response="No relevant legal sources found. Please try rephrasing your question or consult a lawyer directly.",
                citations=[],
                confidence="LOW",
                sources_count=0,
                processing_time_ms=round((time.time() - start_time) * 1000, 2)
            )
        
        # Step 3: Format context for Groq (clean and structured)
        context_parts = []
        for i, (src, meta) in enumerate(zip(results["sources"], results["metadata"]), 1):
            act = meta.get("act_title", "Unknown").lstrip("1")
            section = meta.get("section_label", "")
            section_str = f" - Section {section}" if section and section not in ["General Provision", "Section", ""] else ""
            
            clean_src = src.replace('\n', ' ').replace('\r', ' ').strip()
            clean_src = ' '.join(clean_src.split())
            
            context_parts.append(f"[SOURCE {i}] {act}{section_str}\n{clean_src[:1000]}")
        
        context = "\n\n".join(context_parts)
        
        # Step 4: Detect language for response
        lang = results.get("language", "en")
        
        # Step 5: Build prompts for Groq with DETAILED instructions
        if lang == "bn":
            system_prompt = """আপনি LegalEase BD, বাংলাদেশী আইনের একটি AI সহকারী।

কঠোর নিয়ম:
১. শুধুমাত্র প্রদত্ত SOURCE থেকে তথ্য ব্যবহার করুন
২. কখনো নিজে থেকে ধারা নম্বর বা শাস্তি তৈরি করবেন না
৩. উৎস থেকে হুবহু উদ্ধৃত করুন
৪. তথ্য না থাকলে বলুন "প্রদত্ত উৎসে উল্লেখ নেই"
৫. সবসময় বাংলায় উত্তর দিন

এই কাঠামোতে বিস্তারিত উত্তর দিন:
📘 ব্যাখ্যা: [৪-৬টি বাক্য - বিস্তারিত ব্যাখ্যা]
⚖️ আইনি ভিত্তি: [আইনের নাম, ধারা নম্বর, মূল বিধান]
🪜 পরবর্তী পদক্ষেপ: [অন্তত ৪টি ধাপ]
📊 আস্থার মাত্রা: [উচ্চ/মাঝারি/নিম্ন]
⚠️ সতর্কতা: [ব্যবহারিক সতর্কতা]"""
            
            user_prompt = f"""SOURCE (শুধুমাত্র এগুলো ব্যবহার করুন):
{context}

প্রশ্ন: {request.query}

বিস্তারিত উত্তর দিন। ব্যাখ্যা বিভাগে ৪-৬টি বাক্য লিখুন। পরবর্তী পদক্ষেপে অন্তত ৪টি ধাপ দিন।"""
        
        else:
            system_prompt = """You are LegalEase BD, an AI legal assistant for Bangladeshi law.

STRICT RULES:
1. ONLY use information from the provided SOURCES
2. NEVER invent laws, sections, or punishments
3. Quote exact wording from sources when possible
4. If information isn't in sources, say "Not specified in provided sources"
5. Respond in the same language as the user's question

Format your answer exactly like this:
📘 EXPLANATION: [4-6 sentences - provide DETAILED explanation]
⚖️ LEGAL BASIS: [Act name, Section number, Key provision quote]
🪜 NEXT STEPS: [At least 4 concrete actions]
📊 CONFIDENCE: [HIGH/MEDIUM/LOW]
⚠️ WARNING: [Practical caution - mention consulting a lawyer if serious]"""
            
            user_prompt = f"""SOURCES (use only these):
{context}

QUESTION: {request.query}

Provide a DETAILED answer. For the EXPLANATION section, write 4-6 comprehensive sentences. 
For NEXT STEPS, provide at least 4 concrete actions.

Answer using the format above. Be accurate and helpful."""
        
        # Step 6: Call Groq API
        print("🤖 Calling Groq API...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            groq_response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1500,
                    "top_p": 0.9
                }
            )
            
            if groq_response.status_code == 200:
                answer = groq_response.json()["choices"][0]["message"]["content"]
            else:
                error_text = groq_response.text[:200]
                print(f"Groq error: {groq_response.status_code} - {error_text}")
                answer = f"⚠️ Groq API error: {groq_response.status_code}\n\nHere are the relevant legal sources:\n\n{context}"
        
        # Step 7: Build citations
        citations = results.get("citations", [])
        if not citations:
            seen = set()
            for meta in results.get("metadata", [])[:5]:
                act = meta.get("act_title", "Unknown").lstrip("1")
                if act not in seen:
                    seen.add(act)
                    citations.append({
                        "act": act,
                        "act_no": meta.get("act_no", ""),
                        "year": meta.get("act_year", ""),
                        "section": meta.get("section_label", ""),
                    })
        
        # Step 8: Use pre-computed confidence from modal_llm
        confidence = results.get("confidence", "LOW")
        
        processing_ms = round((time.time() - start_time) * 1000, 2)
        print(f"✅ Complete in {processing_ms}ms")
        
        return QueryResponse(
            query=request.query,
            language=lang,
            response=answer,
            citations=citations[:5],
            confidence=confidence,
            sources_count=len(results.get("sources", [])),
            processing_time_ms=processing_ms
        )
    
    return web_app

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         LegalEase BD - FastAPI Gateway                       ║
    ║  Deploy with:                                                ║
    ║    modal deploy modal_fastapi.py                             ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
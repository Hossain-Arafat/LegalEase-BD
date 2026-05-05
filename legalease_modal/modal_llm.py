# modal_llm.py - Complete LegalEase BD with full notebook features
import modal
from modal import App, Image, Volume, method, enter
import re
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

app = modal.App("legalease-llm")

# Comprehensive image with all dependencies
llm_image = (
    Image.from_registry("python:3.11-slim")
    .apt_install("gcc", "g++", "python3-dev", "git", "build-essential")
    .pip_install(
        "sentence-transformers==2.2.2",
        "chromadb>=0.5.0",
        "rank-bm25==0.2.2",
        "numpy==1.23.5",
        "torch==2.0.1",
        "tqdm==4.66.1",
        "transformers==4.36.0",
        "accelerate==0.25.0",
        "huggingface-hub==0.19.4",
    )
)

volume = Volume.from_name("legalease-data", create_if_missing=True)


@dataclass
class QueryIntent:
    domain: str
    query_type: str
    religion: Optional[str]
    urgency: str
    confidence: float
    raw_query: str
    act_filter_hints: List[str]


@app.cls(
    image=llm_image,
    volumes={"/data": volume},
    scaledown_window=60,
    memory=16384,
    gpu="T4",
)
class LegalEaseLLM:
    
    @enter()
    def load(self):
        from sentence_transformers import SentenceTransformer
        import chromadb
        import pickle
        import torch
        
        print("\n" + "="*60)
        print("🚀 LegalEase BD - Loading Complete System")
        print("="*60)
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"📍 Device: {self.device}")
        
        # 1. Load ChromaDB
        print("\n📚 Loading ChromaDB...")
        chroma_path = "/data/indexes/chroma_db"
        
        try:
            self.chroma = chromadb.PersistentClient(path=chroma_path)
            collections = self.chroma.list_collections()
            print(f"   Available collections: {[c.name for c in collections]}")
            self.collection = self.chroma.get_collection("legalease_final")
            print(f"   ✅ {self.collection.count()} vectors loaded")
        except Exception as e:
            print(f"   ❌ ChromaDB error: {e}")
            try:
                self.chroma.delete_collection("legalease_final")
            except:
                pass
            self.collection = self.chroma.create_collection("legalease_final")
            print(f"   ✅ Created new collection")
        
        # 2. Load BM25
        print("\n📊 Loading BM25...")
        bm25_path = "/data/indexes/bm25_final.pkl"
        
        try:
            with open(bm25_path, "rb") as f:
                bm25_data = pickle.load(f)
            self.bm25 = bm25_data["bm25"]
            self.en_chunks = bm25_data.get("en_chunks", [])
            self.bn_chunks = bm25_data.get("bn_chunks", [])
            print(f"   ✅ BM25 loaded - {len(self.en_chunks)} English chunks")
            print(f"   ✅ {len(self.bn_chunks)} Bengali chunks (semantic only)")
        except Exception as e:
            print(f"   ⚠️ BM25 error: {e}")
            self.bm25 = None
            self.en_chunks = []
            self.bn_chunks = []
        
        # 3. Load Embedding Model
        print("\n🔤 Loading embedding model...")
        self.embedder = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            device=self.device
        )
        print(f"   ✅ Embedder loaded")
        
        # 4. Complete Legal Stopwords (from notebook)
        self.legal_stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "as", "is", "are", "was",
            "were", "be", "been", "being", "have", "has", "had", "do", "does",
            "did", "will", "would", "could", "should", "may", "might",
            "can", "this", "that", "these", "those", "it", "its", "not",
            "what", "which", "who", "whom", "how", "when", "where", "why",
            "act", "rules", "section", "sub", "clause", "provisions",
            "under", "pursuant", "hereby", "herein", "thereof", "therein",
            "notwithstanding", "accordance", "aforesaid", "said",
            "every", "any", "all", "such", "other", "following",
            "provided", "order", "government", "bangladesh",
            "authority", "person", "persons", "shall", "also",
        }
        
        # 5. Complete Domain Rules (from notebook)
        self.domain_rules = {
            "family_law": {
                "keywords": [
                    "divorce", "marriage", "talaq", "nikah", "dower", "mehr",
                    "custody", "guardian", "maintenance", "alimony", "matrimonial",
                    "husband", "wife", "widow", "dowry", "inheritance", "succession",
                    "heir", "family", "child support", "polygamy",
                    "তালাক", "বিবাহ", "বিবাহবিচ্ছেদ", "দেনমোহর", "খোরপোশ",
                    "অভিভাবক", "উত্তরাধিকার", "যৌতুক", "স্ত্রী", "স্বামী",
                    "সন্তান", "বিধবা", "পরিবার", "বহুবিবাহ",
                ],
                "act_hints": [
                    "family", "marriage", "divorce", "muslim family",
                    "hindu", "succession", "guardian", "dowry", "women", "married women",
                ],
            },
            "criminal_law": {
                "keywords": [
                    "murder", "robbery", "theft", "rape", "assault", "dacoity",
                    "arrest", "bail", "detention", "prison", "punishment",
                    "imprisonment", "fine", "offence", "crime", "criminal",
                    "police", "fir", "complaint", "warrant", "remand",
                    "homicide", "culpable", "extortion", "kidnap", "abduction",
                    "হত্যা", "ডাকাতি", "চুরি", "ধর্ষণ", "গ্রেফতার", "জামিন",
                    "কারাদণ্ড", "শাস্তি", "অপরাধ", "পুলিশ", "মামলা",
                ],
                "act_hints": [
                    "penal code", "criminal procedure", "evidence",
                    "special powers", "arms", "explosive", "narcotic",
                ],
            },
            "property_law": {
                "keywords": [
                    "land", "property", "registration", "deed", "title",
                    "tenancy", "rent", "lease", "mortgage", "eviction",
                    "khatian", "mutation", "cadastral", "immovable",
                    "transfer", "conveyance", "plot", "boundary",
                    "জমি", "ভূমি", "সম্পত্তি", "নিবন্ধন", "দলিল",
                    "খতিয়ান", "ইজারা", "বন্ধক", "উচ্ছেদ", "মালিকানা",
                ],
                "act_hints": [
                    "registration", "transfer of property", "tenancy",
                    "land", "acquisition", "revenue",
                ],
            },
            "corporate_law": {
                "keywords": [
                    "company", "corporation", "incorporate", "memorandum",
                    "articles", "shareholder", "director", "partnership",
                    "trade", "business", "trademark", "copyright", "patent",
                    "contract", "agreement", "arbitration", "insolvency",
                    "bankruptcy", "license",
                    "কোম্পানি", "ব্যবসা", "চুক্তি", "অংশীদারিত্ব",
                    "ট্রেডমার্ক", "লাইসেন্স", "দেউলিয়া",
                ],
                "act_hints": [
                    "companies", "partnership", "trade", "contract",
                    "arbitration", "insolvency", "copyright", "trademark",
                ],
            },
            "labour_law": {
                "keywords": [
                    "worker", "employee", "employer", "labour", "wages",
                    "salary", "factory", "termination", "dismissal",
                    "leave", "maternity", "provident fund", "gratuity",
                    "strike", "union", "workmen", "compensation",
                    "শ্রমিক", "কর্মী", "মজুরি", "কারখানা", "ছাঁটাই",
                    "ছুটি", "ট্রেড ইউনিয়ন", "ক্ষতিপূরণ",
                ],
                "act_hints": [
                    "labour", "factory", "workmen", "employment",
                    "industrial", "wages", "labor",
                ],
            },
            "constitutional_law": {
                "keywords": [
                    "fundamental rights", "constitution", "citizenship",
                    "parliament", "government", "election", "court",
                    "high court", "supreme court", "writ", "habeas corpus",
                    "right to", "freedom of", "equality",
                    "সংবিধান", "মৌলিক অধিকার", "নাগরিকত্ব", "সংসদ",
                    "নির্বাচন", "আদালত", "রিট",
                ],
                "act_hints": [
                    "constitution", "citizenship", "election",
                    "representation", "civil rights",
                ],
            },
        }
        
        # 6. Query Type Rules (from notebook)
        self.query_type_rules = {
            "punishment": [
                "punishment", "penalty", "sentence", "imprisonment", "fine",
                "শাস্তি", "দণ্ড", "কারাদণ্ড",
                "how many years", "what happens if",
            ],
            "procedure": [
                "how to", "process", "procedure", "steps", "file", "apply",
                "register", "submit", "obtain", "get", "acquire",
                "কীভাবে", "প্রক্রিয়া", "পদ্ধতি", "আবেদন",
            ],
            "rights": [
                "rights", "entitled", "can i", "allowed", "legal right",
                "what are my", "what is my",
                "অধিকার", "পাওনা", "দাবি",
            ],
            "definition": [
                "what is", "define", "meaning", "definition", "what does",
                "কী", "কি", "সংজ্ঞা", "অর্থ",
            ],
            "eligibility": [
                "eligible", "qualify", "who can", "can i", "am i",
                "requirements", "conditions", "criteria",
                "যোগ্যতা", "শর্ত",
            ],
        }
        
        # 7. Religion Keywords (from notebook)
        self.religion_keywords = {
            "muslim": [
                "muslim", "islam", "talaq", "nikah", "mehr", "dower",
                "muslim family", "mahr", "iddat", "sharia",
                "মুসলিম", "ইসলাম", "তালাক", "নিকাহ", "মোহর",
            ],
            "hindu": [
                "hindu", "hinduism", "brahmin", "caste", "dayabhaga",
                "mitakshara", "sapinda",
                "হিন্দু",
            ],
            "christian": [
                "christian", "church", "baptism", "parish",
                "খ্রিস্টান",
            ],
        }
        
        # 8. Urgency Keywords (from notebook)
        self.urgency_keywords = [
            "arrested", "arrest", "detained", "detention", "jail", "prison",
            "bail", "emergency", "urgent", "immediately", "right now",
            "গ্রেফতার", "জামিন", "জরুরি", "এখনই",
        ]
        
        # 9. Complete Query Expansion Map (from notebook)
        self.expansion_map = {
            "divorce": ["divorce", "talaq", "dissolution", "matrimonial"],
            "marriage": ["marriage", "matrimonial", "nikah", "solemnization"],
            "land": ["land", "tenancy", "khatian", "deed", "immovable"],
            "registration": ["registration", "registrar", "registered"],
            "company": ["company", "corporation", "incorporation", "memorandum"],
            "robbery": ["robbery", "dacoity", "theft", "extortion"],
            "murder": ["murder", "culpable", "homicide"],
            "bail": ["bail", "custody", "detention", "remand"],
            "property": ["property", "ownership", "possession", "immovable"],
            "inheritance": ["inheritance", "succession", "intestate", "heir", "bequest"],
            "women": ["women", "wife", "widow", "dowry", "dower", "mehr"],
            "child": ["child", "minor", "guardian", "juvenile"],
            "labour": ["labour", "worker", "employment", "wages"],
            "tax": ["tax", "income", "revenue", "assessment"],
            "contract": ["contract", "agreement", "breach"],
            "rent": ["rent", "tenant", "landlord", "lease", "eviction"],
            "loan": ["loan", "mortgage", "debt", "creditor"],
            "rape": ["rape", "assault", "outrage", "modesty", "sexual"],
            "will": ["will", "testament", "probate", "executor", "bequest"],
            "adoption": ["adoption", "guardian", "ward", "minor"],
            "arbitration": ["arbitration", "award", "tribunal", "dispute"],
            "insurance": ["insurance", "policy", "indemnity", "premium"],
            "copyright": ["copyright", "intellectual", "trademark", "patent"],
            "environment": ["environment", "pollution", "conservation", "forest"],
        }
        
        # 10. Complete Bengali to English Legal Terms (from notebook)
        self.bn_to_en = {
            # Family law
            "তালাক": "divorce talaq",
            "বিবাহ": "marriage",
            "বিবাহবিচ্ছেদ": "divorce dissolution marriage",
            "দেনমোহর": "dower mehr",
            "খোরপোশ": "maintenance alimony",
            "সন্তানের": "child custody",
            "অভিভাবকত্ব": "guardianship custody minor",
            "উত্তরাধিকার": "inheritance succession",
            "বহুবিবাহ": "polygamy",
            # Property
            "জমি": "land property",
            "জমির": "land property",
            "ভূমি": "land property",
            "নিবন্ধন": "registration",
            "দলিল": "deed document",
            "মালিকানা": "ownership title",
            "ইজারা": "lease",
            "বন্ধক": "mortgage",
            # Criminal
            "ডাকাতি": "robbery dacoity",
            "ডাকাতির": "robbery dacoity",
            "হত্যা": "murder homicide",
            "ধর্ষণ": "rape assault",
            "চুরি": "theft",
            "জামিন": "bail",
            "গ্রেফতার": "arrest detention",
            "শাস্তি": "punishment imprisonment",
            "কারাদণ্ড": "imprisonment",
            # Women's rights
            "নারীর": "women female",
            "নারী": "women female",
            "স্ত্রীর": "wife woman",
            "বিধবা": "widow",
            "যৌতুক": "dowry",
            "সম্পত্তি": "property",
            "অধিকার": "rights",
            # Corporate
            "কোম্পানি": "company corporation",
            "কোম্পানির": "company corporation",
            "ব্যবসা": "business",
            "অংশীদারিত্ব": "partnership",
            "চুক্তি": "contract agreement",
            # Labour
            "শ্রমিক": "worker labour",
            "কর্মী": "employee worker",
            "মজুরি": "wages salary",
            "ছাঁটাই": "termination dismissal",
            # General
            "আইন": "law act",
            "আদালত": "court",
            "মামলা": "case suit",
            "বিচার": "trial judgment",
            "আপিল": "appeal",
            "ক্ষতিপূরণ": "compensation damages",
            "লাইসেন্স": "license",
            "পেনশন": "pension",
            "কর": "tax",
        }
        
        self.is_ready = True
        print("\n" + "="*60)
        print("✅ LegalEase BD COMPLETE SYSTEM READY!")
        print(f"   - Device: {self.device}")
        print(f"   - Domains: {len(self.domain_rules)}")
        print(f"   - Query types: {len(self.query_type_rules)}")
        print(f"   - Expansion terms: {len(self.expansion_map)}")
        print(f"   - BN→EN terms: {len(self.bn_to_en)}")
        print("="*60 + "\n")
    
    # ============================================================
    # Language & Helper Functions
    # ============================================================
    
    def detect_language(self, text: str) -> str:
        bengali_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
        return "bn" if bengali_chars > 2 else "en"
    
    def tokenize_for_bm25(self, text: str):
        if not isinstance(text, str):
            text = str(text)
        text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
        return [t for t in text.split() if t not in self.legal_stopwords and len(t) > 2]
    
    # ============================================================
    # Intent Classification (from notebook - complete)
    # ============================================================
    
    def classify_intent(self, query: str) -> QueryIntent:
        q_lower = query.lower()
        
        domain, domain_conf = self._classify_domain(q_lower)
        query_type = self._classify_query_type(q_lower)
        religion = self._classify_religion(q_lower, domain)
        urgency = self._classify_urgency(q_lower)
        act_hints = self.domain_rules.get(domain, {}).get("act_hints", [])
        
        return QueryIntent(
            domain=domain,
            query_type=query_type,
            religion=religion,
            urgency=urgency,
            confidence=domain_conf,
            raw_query=query,
            act_filter_hints=act_hints,
        )
    
    def _classify_domain(self, q: str):
        scores = {}
        for domain, rules in self.domain_rules.items():
            score = sum(1 for kw in rules["keywords"] if kw in q)
            if score > 0:
                scores[domain] = score
        
        if not scores:
            return "general", 0.3
        
        best = max(scores, key=scores.get)
        total_hits = sum(scores.values())
        confidence = min(0.95, 0.5 + (scores[best] / max(total_hits, 1)) * 0.45)
        
        return best, confidence
    
    def _classify_query_type(self, q: str):
        for qtype, keywords in self.query_type_rules.items():
            if any(kw in q for kw in keywords):
                return qtype
        return "general"
    
    def _classify_religion(self, q: str, domain: str):
        if domain != "family_law":
            return None
        for religion, keywords in self.religion_keywords.items():
            if any(kw in q for kw in keywords):
                return religion
        return "general"
    
    def _classify_urgency(self, q: str):
        return "high" if any(kw in q for kw in self.urgency_keywords) else "normal"
    
    # ============================================================
    # Query Expansion & Translation
    # ============================================================
    
    def expand_query(self, query: str) -> str:
        q_lower = query.lower()
        extra_terms = []
        for keyword, related in self.expansion_map.items():
            if keyword in q_lower:
                existing = set(q_lower.split())
                extra_terms.extend([t for t in related if t not in existing])
        if extra_terms:
            return query + " " + " ".join(list(set(extra_terms))[:5])
        return query
    
    def translate_bengali_query(self, query: str) -> str:
        words = query.split()
        english_terms = []
        for word in words:
            clean_word = word.strip("?।,;:!()")
            if clean_word in self.bn_to_en:
                english_terms.append(self.bn_to_en[clean_word])
        if english_terms:
            return query + " " + " ".join(english_terms[:5])
        return query
    
    # ============================================================
    # Domain Filtering & Boosting (from notebook)
    # ============================================================
    
    def _boost_domain_relevant(self, results: List[Dict], intent: QueryIntent, boost: float = 0.05):
        boosted = []
        for r in results:
            act_title = r["metadata"].get("act_title", "").lower()
            bonus = 0.0
            for hint in intent.act_filter_hints:
                if hint.lower() in act_title:
                    bonus = boost
                    break
            boosted.append({
                **r,
                "rrf_score": r.get("rrf_score", r.get("score", 0)) + bonus,
                "boosted": bonus > 0,
            })
        boosted.sort(key=lambda x: x["rrf_score"], reverse=True)
        return boosted
    
    def _domain_filter(self, results: List[Dict], intent: QueryIntent):
        hints = [h.lower() for h in intent.act_filter_hints]
        filtered = [
            r for r in results
            if any(hint in r["metadata"].get("act_title", "").lower() for hint in hints)
        ]
        return filtered if filtered else results
    
    # ============================================================
    # Search Functions (complete hybrid with RRF)
    # ============================================================
    
    def bm25_search(self, query: str, top_k: int = 20):
        if not self.bm25 or not self.en_chunks:
            return []
        expanded = self.expand_query(query)
        tokens = self.tokenize_for_bm25(expanded)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        indexed = [(i, s) for i, s in enumerate(scores) if s > 0]
        indexed.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in indexed[:top_k]:
            chunk = self.en_chunks[idx]
            results.append({
                "text": chunk.get("text", ""),
                "metadata": chunk.get("metadata", {}),
                "score": float(score),
                "rrf_score": float(score),
                "source": "bm25"
            })
        return results
    
    def semantic_search(self, query: str, top_k: int = 20, language_filter: str = None):
        lang = self.detect_language(query)
        if lang == "bn":
            search_query = self.translate_bengali_query(query)
        else:
            search_query = self.expand_query(query)
        
        embedding = self.embedder.encode(search_query, normalize_embeddings=True).tolist()
        
        where_filter = None
        if language_filter:
            where_filter = {"language": {"$eq": language_filter}}
        
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        formatted_results = []
        for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
            formatted_results.append({
                "text": doc,
                "metadata": meta,
                "score": 1.0 - dist,
                "rrf_score": 1.0 - dist,
                "source": "semantic"
            })
        
        return formatted_results
    
    def hybrid_search(self, query: str, top_k: int = 5):
        try:
            lang = self.detect_language(query)
            
            # For Bengali: semantic search only (BM25 unreliable without morphology)
            if lang == "bn":
                augmented_query = self.translate_bengali_query(query)
                results = self.semantic_search(augmented_query, top_k=top_k * 4, language_filter="en")
                intent = self.classify_intent(query)
                results = self._boost_domain_relevant(results, intent)
                
                return {
                    "results": results[:top_k],
                    "sources": [r["text"] for r in results[:top_k]],
                    "metadata": [r["metadata"] for r in results[:top_k]],
                    "scores": [r["rrf_score"] for r in results[:top_k]],
                    "language": lang,
                    "intent": intent
                }
            
            # For English: hybrid search with RRF
            semantic_results = self.semantic_search(query, top_k=top_k * 4, language_filter="en")
            bm25_results = self.bm25_search(query, top_k=top_k * 4)
            
            if not semantic_results and not bm25_results:
                return {
                    "results": [],
                    "sources": [],
                    "metadata": [],
                    "scores": [],
                    "language": lang,
                    "intent": self.classify_intent(query)
                }
            
            # Reciprocal Rank Fusion
            rrf_k = 60
            scores = {}
            chunks = {}
            
            for rank, r in enumerate(semantic_results):
                rrf_score = 1 / (rrf_k + rank + 1)
                chunk_id = r["metadata"].get("chunk_id", f"sem_{rank}")
                scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
                chunks[chunk_id] = r
            
            for rank, r in enumerate(bm25_results):
                rrf_score = 1 / (rrf_k + rank + 1)
                chunk_id = r["metadata"].get("chunk_id", f"bm25_{rank}")
                scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
                if chunk_id not in chunks:
                    chunks[chunk_id] = r
            
            sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            intent = self.classify_intent(query)
            results_with_scores = []
            for chunk_id, rrf_score in sorted_ids[:top_k * 2]:
                chunk = chunks[chunk_id]
                chunk["rrf_score"] = rrf_score
                results_with_scores.append(chunk)
            
            boosted_results = self._boost_domain_relevant(results_with_scores, intent)
            final_results = boosted_results[:top_k]
            
            return {
                "results": final_results,
                "sources": [r["text"] for r in final_results],
                "metadata": [r["metadata"] for r in final_results],
                "scores": [r["rrf_score"] for r in final_results],
                "language": lang,
                "intent": intent
            }
            
        except Exception as e:
            print(f"Search error: {e}")
            return {
                "results": [],
                "sources": [],
                "metadata": [],
                "scores": [],
                "language": "en",
                "intent": QueryIntent("general", "general", None, "normal", 0.3, "", [])
            }
    
    # ============================================================
    # Confidence Scoring (from notebook)
    # ============================================================
    
    def compute_confidence(self, query: str, results: List[Dict], intent: QueryIntent) -> Dict:
        if not results:
            return {"score": 0.0, "label": "LOW", "reason": "No relevant sources found."}
        
        top_score = results[0].get("rrf_score", results[0].get("score", 0))
        second_score = results[1].get("rrf_score", results[1].get("score", 0)) if len(results) > 1 else 0.0
        score_gap = top_score - second_score
        boosted_count = sum(1 for r in results if r.get("boosted", False))
        lang = self.detect_language(query)
        
        # Base score from retrieval strength
        if lang == "en":
            if top_score >= 0.040: base = 0.85
            elif top_score >= 0.028: base = 0.70
            elif top_score >= 0.018: base = 0.50
            else: base = 0.30
        else:
            if top_score >= 0.75: base = 0.85
            elif top_score >= 0.62: base = 0.65
            elif top_score >= 0.50: base = 0.45
            else: base = 0.25
        
        if score_gap > 0.005: base += 0.05
        if boosted_count >= 3: base += 0.05
        elif boosted_count >= 1: base += 0.02
        if intent.domain == "general": base -= 0.15
        
        score = min(0.95, max(0.10, base))
        
        if score >= 0.75:
            label = "HIGH"
            reason = "Answer directly found in retrieved legal sources."
        elif score >= 0.50:
            label = "MEDIUM"
            reason = "Relevant sources found but answer may be partial. Verify with a lawyer."
        else:
            label = "LOW"
            reason = "Sources are indirectly related. Please consult a qualified lawyer."
        
        return {"score": round(score, 2), "label": label, "reason": reason}
    
    # ============================================================
    # Format Context for LLM
    # ============================================================
    
    def format_context(self, results: List[Dict]) -> str:
        parts = []
        for i, r in enumerate(results):
            m = r["metadata"]
        
        # Safe get with defaults
            act_title = m.get("act_title", "Unknown Act")
            act_no = m.get("act_no", "")
            act_year = m.get("act_year", "")
            section = m.get("section_label", "")
            body = m.get("raw_text", r.get("text", ""))
        
        # Build citation safely
            if act_no and act_year:
                act_str = f"{act_title} (Act {act_no} of {act_year})"
            elif act_no:
                act_str = f"{act_title} (Act {act_no})"
            elif act_year:
                act_str = f"{act_title} ({act_year})"
            else:
                act_str = act_title
        
            skip_labels = {"General Provision", "Subsection (1)", "Section", ""}
            sec_str = f" — {section}" if section and section not in skip_labels else ""
        
            parts.append(
                f"[SOURCE {i+1}]\n"
                f"Citation: {act_str}{sec_str}\n"
                f"Text: {body}"
            )
    
        separator = "\n\n" + "─" * 60 + "\n\n"
        return separator.join(parts)

    # ============================================================
    # Main Public Methods
    # ============================================================
    
    @method()
    def search(self, question: str, top_k: int = 5, use_llm: bool = False) -> dict:
        """Complete search with intent classification, boosting, and confidence scoring"""
        
        search_result = self.hybrid_search(question, top_k=top_k)
        results = search_result["results"]
        intent = search_result["intent"]
        
        if not results:
            return {
                "query": question,
                "language": search_result["language"],
                "response": "",
                "sources": [],
                "metadata": [],
                "scores": [],
                "citations": [],
                "confidence": "LOW",
                "intent": intent.__dict__ if intent else None,
                "status": "no_results"
            }
        
        confidence = self.compute_confidence(question, results, intent)
        
        citations = []
        seen = set()
        for meta in [r["metadata"] for r in results[:5]]:
            act = meta.get("act_title", "Unknown").lstrip("1")
            if act not in seen:
                seen.add(act)
                citations.append({
                    "act": act,
                    "act_no": meta.get("act_no", ""),
                    "year": meta.get("act_year", ""),
                    "section": meta.get("section_label", ""),
                    "source_url": meta.get("source_url", ""),
                })
        
        context = self.format_context(results)
        
        return {
            "query": question,
            "language": search_result["language"],
            "response": "",
            "sources": [r["text"] for r in results],
            "metadata": [r["metadata"] for r in results],
            "scores": [r.get("rrf_score", r.get("score", 0)) for r in results],
            "citations": citations,
            "context": context,
            "confidence": confidence["label"],
            "confidence_details": confidence,
            "intent": {
                "domain": intent.domain,
                "query_type": intent.query_type,
                "religion": intent.religion,
                "urgency": intent.urgency,
                "confidence": intent.confidence,
                "act_filter_hints": intent.act_filter_hints,
            } if intent else None,
            "sources_count": len(results),
            "top_score": max([r.get("rrf_score", r.get("score", 0)) for r in results]),
            "status": "success"
        }
    
    @method()
    def health(self) -> dict:
        return {
            "status": "healthy",
            "device": self.device,
            "vectors": self.collection.count() if hasattr(self, 'collection') and self.collection else 0,
            "bm25_chunks": len(self.en_chunks) if hasattr(self, 'en_chunks') else 0,
            "bn_chunks": len(self.bn_chunks) if hasattr(self, 'bn_chunks') else 0,
            "domains_available": len(self.domain_rules),
            "query_types": len(self.query_type_rules),
            "expansion_terms": len(self.expansion_map),
            "bn_translations": len(self.bn_to_en),
        }


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     LegalEase BD - Complete Modal Deployment                 ║
    ║                                                              ║
    ║  All features from notebook now in Modal:                    ║
    ║    ✅ Intent Classification (6 domains)                      ║
    ║    ✅ Query Type Detection (5 types)                         ║
    ║    ✅ Religion Detection (Muslim/Hindu/Christian)            ║
    ║    ✅ Urgency Detection                                      ║
    ║    ✅ Complete Legal Stopwords (50+ terms)                   ║
    ║    ✅ 24+ Query Expansion Terms                              ║
    ║    ✅ 45+ Bengali→English Translations                       ║
    ║    ✅ Domain Boosting & Filtering                            ║
    ║    ✅ Confidence Scoring (HIGH/MEDIUM/LOW)                   ║
    ║    ✅ Hybrid Search with RRF                                 ║
    ║                                                              ║
    ║  Deploy with:                                                ║
    ║    modal deploy modal_llm.py                                 ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

# Product Requirements Document (PRD)

## Groww RAG Chatbot


| Field                | Detail              |
| -------------------- | ------------------- |
| **Product Name**     | Groww RAG Chatbot   |
| **Document Version** | 1.0                 |
| **Date**             | 2026-09-27          |
| **Author**           | Pooja Jaiswal       |
| **Status**           | Draft               |
| **Target Demo**      | Class Demonstration |


---

## 1. Executive Summary

The Groww RAG Chatbot is a Retrieval-Augmented Generation (RAG) based conversational AI application designed to answer user queries about the Groww investment platform, stock market concepts, mutual funds, and related financial topics. The chatbot leverages a knowledge base of curated documents to provide accurate, contextually relevant responses, making it an effective educational tool for a class demonstration on RAG architecture and LLM-powered applications.

---



## 2. Problem Statement



### 2.1 Background

Groww is one of India's largest retail investment platforms, offering services in stocks, mutual funds, ETFs, IPOs, and more. New users often face a steep learning curve when navigating the platform and understanding financial concepts. Existing support channels (help centers, FAQs) are static and do not provide personalized, conversational assistance.

### 2.2 Problem

- Users struggle to find relevant information quickly across scattered help articles and documentation.
- Static FAQs cannot handle nuanced or multi-turn questions.
- There is no interactive way for new users to learn about Groww's features and stock market investing in a conversational manner.
- For educational purposes, there is no demonstration tool that showcases how RAG pipelines work in a real-world financial domain.



### 2.3 Opportunity

Build a RAG-powered chatbot that:

- Ingests Groww-related documents (help articles, FAQs, product descriptions, financial glossary).
- Retrieves relevant context in response to user queries.
- Generates coherent, accurate, and cited responses using an LLM.
- Serves as a compelling class demo illustrating the full RAG pipeline: document ingestion → chunking → embedding → vector storage → retrieval → generation.

---



## 3. Goals & Objectives



### 3.1 Primary Goals


| #   | Goal                                                                | Success Metric                                                      |
| --- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| G1  | Build a functional RAG chatbot that answers Groww-related questions | ≥ 80% answer relevance on a test query set                          |
| G2  | Demonstrate the complete RAG pipeline in a class setting            | Live demo with < 5s response time                                   |
| G3  | Provide source citations for generated answers                      | 100% of responses include retrievable source references             |
| G4  | Create an intuitive, chat-based UI                                  | User can ask a question and receive an answer within 2 interactions |




### 3.2 Secondary Goals

- Support multi-turn conversations with context retention.
- Handle out-of-scope queries gracefully (fallback response).
- Allow easy addition of new documents to the knowledge base.
- Showcase the RAG architecture visually (optional diagram or pipeline view).



### 3.3 Non-Goals

- Real-time stock price lookup or trading functionality.
- User authentication or account management.
- Integration with Groww's production APIs.
- Multi-language support (English only for the demo).
- Mobile app deployment (web-only).

---



## 4. Target Audience


| Audience      | Description                                                         |
| ------------- | ------------------------------------------------------------------- |
| **Primary**   | Students and instructor for class demonstration of RAG architecture |
| **Secondary** | New Groww users seeking platform guidance (simulated)               |
| **Tertiary**  | Developers learning RAG implementation patterns                     |


---



## 5. Scope



### 5.1 In Scope

- Document ingestion pipeline (PDF, TXT, Markdown, web pages).
- Text chunking and embedding generation.
- Vector database storage and similarity search.
- LLM-based response generation with retrieved context.
- Simple web-based chat interface.
- Source citation display.
- Basic conversation history (session-based).
- Fallback handling for irrelevant or out-of-scope queries.



### 5.2 Out of Scope

- Real-time market data integration.
- User accounts, authentication, or personalization.
- Trading or transactional capabilities.
- Voice input/output.
- Mobile-responsive native apps.
- Advanced RAG techniques (hybrid search, re-ranking, query decomposition) — may be mentioned as future work.

---



## 6. User Stories


| ID   | User Story                                                                                                                     | Priority |
| ---- | ------------------------------------------------------------------------------------------------------------------------------ | -------- |
| US-1 | As a student, I want to ask a question about Groww's features so that I can understand how the platform works                  | P0       |
| US-2 | As a student, I want to see which documents the answer was based on so that I can verify the information                       | P0       |
| US-3 | As a student, I want to ask follow-up questions so that I can explore a topic in depth                                         | P1       |
| US-4 | As a student, I want the chatbot to tell me when it doesn't know something so that I am not misled                             | P1       |
| US-5 | As a demonstrator, I want to add new documents to the knowledge base so that I can expand the chatbot's knowledge              | P1       |
| US-6 | As a student, I want a clean, simple chat interface so that I can focus on the conversation                                    | P0       |
| US-7 | As a demonstrator, I want to see the RAG pipeline stages (retrieved chunks, embeddings) so that I can explain the architecture | P2       |


---



## 7. Functional Requirements



### 7.1 Document Ingestion


| ID   | Requirement                                                                                                                            | Priority |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| FR-1 | The system shall accept documents in PDF, TXT, and Markdown formats                                                                    | P0       |
| FR-2 | The system shall extract raw text from uploaded documents                                                                              | P0       |
| FR-3 | The system shall chunk extracted text into segments of 300–500 tokens with 10–20% overlap                                              | P0       |
| FR-4 | The system shall generate embeddings for each chunk using a pre-trained embedding model (e.g., sentence-transformers/all-MiniLM-L6-v2) | P0       |
| FR-5 | The system shall store embeddings and chunk metadata in a vector database (e.g., ChromaDB, FAISS, or Pinecone)                         | P0       |




### 7.2 Query Processing & Retrieval


| ID   | Requirement                                                                                                          | Priority |
| ---- | -------------------------------------------------------------------------------------------------------------------- | -------- |
| FR-6 | The system shall accept free-text user queries via a chat input field                                                | P0       |
| FR-7 | The system shall embed the user query using the same embedding model as the documents                                | P0       |
| FR-8 | The system shall perform a similarity search (cosine similarity) and retrieve the top-K most relevant chunks (K=3–5) | P0       |
| FR-9 | The system shall pass the retrieved chunks as context to the LLM along with the user query                           | P0       |




### 7.3 Response Generation


| ID    | Requirement                                                                                                                                               | Priority |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| FR-10 | The system shall generate a response using an LLM (e.g., GPT-4, GPT-3.5, or an open-source alternative like Llama 3) conditioned on the retrieved context | P0       |
| FR-11 | The system shall display the generated response in the chat interface                                                                                     | P0       |
| FR-12 | The system shall display the source document(s) and chunk(s) used to generate the answer                                                                  | P0       |
| FR-13 | The system shall include a fallback response when no relevant chunks are retrieved (similarity score below threshold)                                     | P1       |
| FR-14 | The system shall maintain conversation history within a session for context-aware follow-up questions                                                     | P1       |




### 7.4 User Interface


| ID    | Requirement                                                                                   | Priority |
| ----- | --------------------------------------------------------------------------------------------- | -------- |
| FR-15 | The system shall provide a web-based chat interface with a message input area and send button | P0       |
| FR-16 | The system shall display user messages and bot responses in a conversational bubble format    | P0       |
| FR-17 | The system shall show a loading/typing indicator while the bot is generating a response       | P1       |
| FR-18 | The system shall provide a "Clear Chat" button to reset the conversation                      | P2       |
| FR-19 | The system shall display retrieved source chunks in an expandable/collapsible section         | P2       |


---



## 8. Non-Functional Requirements


| ID     | Requirement                        | Target                                                          |
| ------ | ---------------------------------- | --------------------------------------------------------------- |
| NFR-1  | Response latency (query to answer) | < 5 seconds (P95)                                               |
| NFR-2  | Concurrent users (demo scenario)   | 1–5 users                                                       |
| NFR-3  | Knowledge base size (initial)      | 10–50 documents                                                 |
| NFR-4  | Embedding model                    | sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)         |
| NFR-5  | Vector database                    | ChromaDB (local) or FAISS                                       |
| NFR-6  | LLM                                | GPT-4o-mini or Llama 3 8B (configurable)                        |
| NFR-7  | Application framework              | Python (FastAPI backend + React/Streamlit frontend)             |
| NFR-8  | Deployment                         | Local machine or cloud VM for demo                              |
| NFR-9  | Availability                       | 99% during demo sessions                                        |
| NFR-10 | Data privacy                       | No user data persisted beyond session; documents are pre-vetted |


---



## 9. System Architecture



### 9.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Interface                        │
│              (Streamlit / React Chat UI)                  │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   API Layer (FastAPI)                     │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  /chat      │  │  /ingest     │  │  /health      │  │
│  │  endpoint   │  │  endpoint    │  │  endpoint     │  │
│  └──────┬──────┘  └──────┬───────┘  └───────────────┘  │
└─────────┼─────────────────┼─────────────────────────────┘
          │                 │
          ▼                 ▼
┌─────────────────┐  ┌──────────────────────────────────┐
│  Query Pipeline │  │     Ingestion Pipeline            │
│  1. Embed query │  │  1. Parse document                │
│  2. Retrieve    │  │  2. Chunk text                    │
│     top-K       │  │  3. Generate embeddings           │
│  3. Generate    │  │  4. Store in vector DB            │
│     response    │  └──────────────────────────────────┘
│  4. Return +    │
│     sources     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              Vector Database (ChromaDB)                   │
│         (Embeddings + Chunk Text + Metadata)             │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              LLM (OpenAI / Ollama / HF)                   │
│         (Response generation with context)               │
└─────────────────────────────────────────────────────────┘
```



### 9.2 RAG Pipeline Flow

1. **Ingestion Phase:**
  - Document → Text Extraction → Chunking → Embedding → Vector DB Storage
2. **Query Phase:**
  - User Query → Query Embedding → Similarity Search → Top-K Chunks Retrieved → Prompt Construction (Query + Context) → LLM Generation → Response + Sources

---



## 10. Technology Stack


| Layer                | Technology                                | Justification                                              |
| -------------------- | ----------------------------------------- | ---------------------------------------------------------- |
| **Frontend**         | Streamlit or React                        | Streamlit for rapid prototyping; React for polished UI     |
| **Backend**          | FastAPI                                   | Lightweight, async, easy to integrate with Python ML stack |
| **Embedding Model**  | sentence-transformers/all-MiniLM-L6-v2    | Small (80MB), fast, good quality for semantic search       |
| **Vector DB**        | ChromaDB                                  | Simple, local, Python-native, persistent storage           |
| **LLM**              | OpenAI GPT-4o-mini or Ollama (Llama 3 8B) | GPT-4o-mini for quality; Ollama for offline/local demo     |
| **Orchestration**    | LangChain or LlamaIndex                   | Simplifies RAG pipeline construction                       |
| **Document Parsing** | PyPDF2, python-docx, unstructured         | Multi-format document ingestion                            |
| **Deployment**       | Local / Docker                            | Simple deployment for class demo                           |


---



## 11. Data Requirements



### 11.1 Knowledge Base Documents


| Category           | Example Documents                                        | Count               |
| ------------------ | -------------------------------------------------------- | ------------------- |
| Groww Help Center  | Account setup, KYC, fund transfers, trading guides       | 10–20               |
| Product Pages      | Stocks, Mutual Funds, ETFs, IPOs, F&O descriptions       | 5–10                |
| Financial Glossary | Terms like "bull market", "P/E ratio", "diversification" | 5–10                |
| FAQs               | Common questions about Groww platform                    | 5–10                |
| **Total**          |                                                          | **25–50 documents** |




### 11.2 Data Format

- All documents stored as plain text or structured Markdown after ingestion.
- Metadata tracked: document title, source URL/file, ingestion date, chunk index.

---



## 12. User Interface Design



### 12.1 Wireframe (Text Description)

```
┌──────────────────────────────────────────────┐
│  Groww RAG Chatbot                           │
│  ─────────────────────────────────────────── │
│                                              │
│  🤖 Hello! I'm the Groww assistant. Ask me  │
│     anything about investing or the Groww    │
│     platform.                                │
│                                              │
│                    ┌──────────────────────┐  │
│                    │ How do I start       │  │
│                    │ investing in stocks? │  │
│                    └──────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ To start investing in stocks on Groww: │  │
│  │ 1. Complete your KYC...                │  │
│  │ 2. Link your bank account...           │  │
│  │ 3. Search for a stock...               │  │
│  │                                        │  │
│  │ 📚 Sources:                            │  │
│  │  • [Groww Help - Stock Trading Guide]  │  │
│  │  • [Groww FAQ - Account Setup]         │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │ Type your question...          [Send]│    │
│  └──────────────────────────────────────┘    │
│                                              │
│  [Clear Chat]                                │
└──────────────────────────────────────────────┘
```



### 12.2 UI Requirements

- Clean, modern chat interface with Groww brand colors (green/blue theme).
- User messages right-aligned; bot responses left-aligned.
- Source citations displayed as clickable links or document names.
- Loading indicator (animated dots or spinner) during response generation.
- Responsive layout (works on laptop screen for demo).

---



## 13. API Design



### 13.1 Endpoints


| Method   | Endpoint              | Description                                              |
| -------- | --------------------- | -------------------------------------------------------- |
| `POST`   | `/api/chat`           | Submit a query and receive a generated response          |
| `POST`   | `/api/ingest`         | Upload and ingest a new document into the knowledge base |
| `GET`    | `/api/health`         | Health check — returns system status                     |
| `GET`    | `/api/documents`      | List all ingested documents                              |
| `DELETE` | `/api/documents/{id}` | Remove a document and its chunks from the vector DB      |




### 13.2 `/api/chat` Request/Response

**Request:**

```json
{
  "query": "How do I buy my first stock on Groww?",
  "session_id": "demo-session-001",
  "conversation_history": [
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello! How can I help you?"}
  ]
}
```

**Response:**

```json
{
  "response": "To buy your first stock on Groww, follow these steps:\n1. Complete your KYC verification...\n2. Add funds to your Groww account...\n3. Search for the stock you want to buy...\n4. Place a buy order...",
  "sources": [
    {
      "document_title": "Groww Help - Stock Trading Guide",
      "chunk_index": 3,
      "similarity_score": 0.87
    },
    {
      "document_title": "Groww FAQ - Getting Started",
      "chunk_index": 1,
      "similarity_score": 0.82
    }
  ],
  "session_id": "demo-session-001"
}
```

---



## 14. Error Handling


| Scenario                     | Handling                                                                                                                   |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| No relevant chunks retrieved | Return fallback: "I'm sorry, I couldn't find relevant information in my knowledge base. Could you rephrase your question?" |
| LLM API failure              | Return: "I'm having trouble generating a response right now. Please try again in a moment."                                |
| Document ingestion failure   | Log error, return error message to admin, skip malformed documents                                                         |
| Empty query                  | Return: "Please enter a question."                                                                                         |
| Vector DB unavailable        | Return system error, suggest retry                                                                                         |


---



## 15. Testing Strategy


| Test Type             | Description                                                              |
| --------------------- | ------------------------------------------------------------------------ |
| **Unit Tests**        | Chunking logic, embedding generation, similarity search                  |
| **Integration Tests** | Full RAG pipeline (ingest → query → retrieve → generate)                 |
| **Evaluation**        | Curated set of 20–30 test questions with expected answer topics          |
| **Manual Testing**    | Live demo testing with edge cases (typos, vague questions, out-of-scope) |
| **Performance Test**  | Measure response latency under normal load                               |




### 15.1 Evaluation Metrics


| Metric                      | Target                                  |
| --------------------------- | --------------------------------------- |
| Answer Relevance            | ≥ 80%                                   |
| Source Attribution Accuracy | ≥ 90%                                   |
| Response Latency (P95)      | < 5 seconds                             |
| Fallback Trigger Accuracy   | ≥ 95% (correctly identify out-of-scope) |


---



## 16. Project Plan & Milestones


| Phase                          | Duration | Deliverables                                                       |
| ------------------------------ | -------- | ------------------------------------------------------------------ |
| **Phase 1: Setup & Ingestion** | Week 1   | Project scaffold, document ingestion pipeline, vector DB populated |
| **Phase 2: RAG Pipeline**      | Week 2   | Query embedding, retrieval, LLM integration, response generation   |
| **Phase 3: UI Development**    | Week 3   | Chat interface, source display, conversation history               |
| **Phase 4: Testing & Polish**  | Week 4   | Testing, evaluation, UI polish, demo preparation                   |
| **Phase 5: Demo**              | Week 5   | Live class demonstration                                           |


---



## 17. Risks & Mitigations


| Risk                                | Likelihood | Impact | Mitigation                                                  |
| ----------------------------------- | ---------- | ------ | ----------------------------------------------------------- |
| LLM API costs exceed budget         | Medium     | Medium | Use GPT-4o-mini or free-tier Ollama for demo                |
| Poor retrieval quality              | Medium     | High   | Tune chunk size, overlap, and top-K; add metadata filtering |
| Slow response times                 | Low        | Medium | Use local embedding model; cache frequent queries           |
| Outdated/incorrect source documents | Low        | Medium | Curate and verify knowledge base before demo                |
| Demo environment lacks internet     | High       | High   | Use local LLM (Ollama) and local vector DB                  |


---



## 18. Future Enhancements

- **Hybrid Search:** Combine BM25 keyword search with semantic search for better retrieval.
- **Re-ranking:** Add a cross-encoder re-ranker to improve chunk relevance.
- **Query Decomposition:** Break complex sub-questions into simpler queries.
- **Multi-modal Support:** Ingest and respond to images/charts.
- **User Feedback Loop:** Allow thumbs up/down on responses for continuous improvement.
- **Streaming Responses:** Stream LLM output token-by-token for better UX.
- **Multi-language Support:** Add Hindi and other regional languages.

---



## 19. Appendix



### 19.1 Glossary


| Term          | Definition                                                                           |
| ------------- | ------------------------------------------------------------------------------------ |
| **RAG**       | Retrieval-Augmented Generation — combining information retrieval with LLM generation |
| **Embedding** | Numerical vector representation of text capturing semantic meaning                   |
| **Chunk**     | A segment of text from a document, used as the unit of retrieval                     |
| **Vector DB** | Database optimized for storing and searching high-dimensional vectors                |
| **Top-K**     | The K most similar items returned by a similarity search                             |
| **LLM**       | Large Language Model — AI model trained to generate human-like text                  |




### 19.2 References

- [LangChain RAG Documentation](https://python.langchain.com/docs/tutorials/rag/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Groww Help Center](https://groww.in/help)
- [Sentence Transformers](https://www.sbert.net/)

---

*End of Document*
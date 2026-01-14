# 🇬🇧 UKGC LCCP Regulatory Assistant (RAG API)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![LlamaIndex](https://img.shields.io/badge/LlamaIndex-0.10-orange?logo=llamaindex&logoColor=white)
![NVIDIA NIM](https://img.shields.io/badge/NVIDIA%20NIM-Powered-76B900?logo=nvidia&logoColor=white)
![Status](https://img.shields.io/badge/Status-Live-success)

> **Live Demo (Swagger UI):** [https://ukgc-lccp-rag-api-1.onrender.com/docs](https://ukgc-lccp-rag-api-1.onrender.com/docs)

## 📖 Project Overview

This project is a high-performance **Retrieval-Augmented Generation (RAG)** API designed to assist compliance officers, legal teams, and stakeholders in navigating the **UK Gambling Commission's Licence Conditions and Codes of Practice (LCCP)**.

Regulatory documents are dense, hierarchical, and difficult to search using traditional keyword methods. This application employs **Semantic Search** to understand the *intent* behind a query (e.g., "rules for preventing money laundering") and retrieves precise legal conditions, answering with strict grounding to the source text.

## 🔄 End-to-End Pipeline

This system was built from scratch, moving from raw unstructured data to a production-grade API.

### 1. Data Engineering & Ingestion
*   **Source:** The raw HTML single-page view of the LCCP.
*   **Parsing Strategy:** Built a custom extraction script using `BeautifulSoup4`.
*   **Hierarchy Preservation:** The script detects the document structure (Part → Section → Subsection → Condition) and injects this context into every chunk.
*   **HTML to Markdown:** Converted HTML list structures (`<ul>`, `<ol>`) into Markdown to ensure the LLM correctly interprets numbered regulations.

### 2. Indexing & Embeddings
*   **Vectorization:** Utilized **NVIDIA's `nv-embedqa-e5-v5`** model, which is optimized for retrieval tasks, to convert text chunks into high-dimensional vectors.
*   **Storage:** Persisted the vector index locally to ensure <50ms retrieval times and eliminate re-indexing costs upon server restarts.

### 3. RAG Logic & Inference
*   **Orchestration:** Used **LlamaIndex** to manage the retrieval and query lifecycle.
*   **LLM:** Powered by **Meta Llama 3.3 70B Instruct** (via NVIDIA NIM) for high-accuracy reasoning and adherence to complex instructions.
*   **Prompt Engineering:** Implemented a strict system prompt to prevent hallucination, forcing the model to answer *only* using retrieved context and to cite specific Regulation IDs.

### 4. Deployment
*   **API Layer:** Wrapped the logic in an asynchronous **FastAPI** application.
*   **Hosting:** Containerized and deployed on **Render**.

## 🚀 Key Features

*   **Semantic Understanding:** Finds relevant regulations even if the user uses synonyms (e.g., "under 18s" finds "protection of children").
*   **Grounded Citations:** Every response includes the specific LCCP code (e.g., *Licence Condition 12.1.1*) and a direct link to the legislation.
*   **Asynchronous Architecture:** Built using Python's `async/await` pattern to handle concurrent requests without blocking the server during LLM inference.

## 🧠 Challenges & Learnings

### Challenge 1: Loss of Structural Context
**The Problem:** Standard text extraction flattened HTML lists. For example, a regulation stating "You must do: a) X, b) Y, c) Z" was read by the LLM as a single unstructured sentence, leading to poor answers when users asked for "lists of requirements."
**The Solution:** I integrated `markdownify` into the ingestion pipeline. By converting HTML to Markdown before embedding, the bullet points and numbered lists were preserved. This significantly improved the model's ability to extract specific list items.

### Challenge 2: Model Size vs. Accuracy
**The Problem:** Initial tests using smaller 1B parameter models resulted in "hallucinations" and an inability to follow strict formatting instructions.
**The Solution:** I migrated to **Llama 3.3 70B** via NVIDIA NIM. This provided the reasoning capabilities of a frontier model (like GPT-4) necessary for legal text interpretation, while the serverless NVIDIA infrastructure kept inference speed under 2 seconds.

## 🛠️ Tech Stack

*   **Language:** Python 3.10+
*   **API Framework:** FastAPI
*   **RAG Framework:** LlamaIndex
*   **LLM Provider:** NVIDIA NIM (Serverless)
*   **Data Processing:** BeautifulSoup4, Markdownify
*   **Cloud Platform:** Render

## 💻 Local Installation

To run this API locally:

1.  **Clone the repo**
    ```bash
    git clone https://github.com/rajo69/ukgc-lccp-rag-api.git
    cd ukgc-lccp-rag-api
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv .venv
    # Windows:
    .\.venv\Scripts\activate
    # Mac/Linux:
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Environment Variables**
    Create a `.env` file in the root directory:
    ```env
    NVIDIA_API_KEY=nvapi-your-key-here
    ```

5.  **Run the Server**
    ```bash
    uvicorn main:app --reload
    ```
    Access the documentation at `http://127.0.0.1:8000/docs`.

## 🔌 API Usage

**Endpoint:** `POST /chat`

**Request:**
```json
{
  "question": "What are the rules regarding financial vulnerability checks?"
}
```

**Response:**
```json
{
  "answer": "According to SR Code 3.4.4, licensees must undertake a financial vulnerability check...",
  "sources": [
    {
      "regulation": "SR Code 3.4.4",
      "type": "Social Responsibility Code",
      "link": "https://www.legislation.gov.uk/..."
    }
  ]
}
```

---
*Created by Rajarshi Nandi*

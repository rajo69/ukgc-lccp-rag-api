# 🇬🇧 UKGC LCCP Regulatory Assistant (RAG API)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![LlamaIndex](https://img.shields.io/badge/LlamaIndex-0.10-orange?logo=llamaindex&logoColor=white)
![NVIDIA NIM](https://img.shields.io/badge/NVIDIA%20NIM-Powered-76B900?logo=nvidia&logoColor=white)
![Status](https://img.shields.io/badge/Status-Live-success)

> **Live Demo (Swagger UI):** [https://ukgc-lccp-rag-api-1.onrender.com/docs](https://ukgc-lccp-rag-api-1.onrender.com/docs)

## 📖 Project Overview

This project is a high-performance **Retrieval-Augmented Generation (RAG)** API designed to assist compliance officers and stakeholders in navigating the **UK Gambling Commission's Licence Conditions and Codes of Practice (LCCP)**.

Traditional keyword search fails with complex regulations. This application uses **Semantic Search** to understand the *intent* behind a question (e.g., "marketing rules") and retrieves the specific legal conditions, citing sources accurately.

## 🚀 Key Features

*   **Semantic Search:** Retrieval of relevant regulations using **NVIDIA's nv-embedqa-e5-v5** model.
*   **Accurate Citations:** Every response includes specific LCCP codes (e.g., *Licence Condition 12.1.1*) and links to the source text.
*   **High-Speed Inference:** Powered by **Meta Llama 3.1 8B** via NVIDIA NIM for sub-second text generation.
*   **Asynchronous Architecture:** Built with **FastAPI** using `async/await` to handle concurrent user requests efficiently.
*   **Custom Ingestion Pipeline:** Python scripts to scrape, clean, and chunk the LCCP HTML documents into a vector-ready dataset.

## 🛠️ Tech Stack

*   **Backend Framework:** FastAPI (Python)
*   **Orchestration:** LlamaIndex
*   **LLM & Embeddings:** NVIDIA NIM (Serverless Inference)
*   **Vector Storage:** Local VectorStore (Persisted on disk for fast cold-starts)
*   **Deployment:** Render (Cloud Hosting)

## 🏗️ Architecture

1.  **Ingestion:** Raw HTML LCCP data is parsed, cleaned, and chunked by Regulation ID.
2.  **Embedding:** Text chunks are converted to vectors using `nvidia/nv-embedqa-e5-v5`.
3.  **Indexing:** Vectors are stored in a persistent local index (`/storage`).
4.  **Querying:**
    *   User sends a natural language query via API.
    *   System retrieves the **Top-3** most relevant chunks.
    *   LLM generates a strict answer based *only* on the retrieved context.

## ⚡ Performance Optimizations

To ensure a responsive user experience on a cloud free-tier environment:
*   **Reduced Top-K:** Optimized retrieval to fetch only the top 3 chunks, reducing LLM token load and latency.
*   **Pre-built Index:** The vector index is built once and deployed as a static asset, eliminating the need for expensive re-indexing on server startup.
*   **Async/Await:** Fully asynchronous endpoints prevent blocking during network calls to the AI inference engine.

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
    python main.py
    ```
    Access the documentation at `http://127.0.0.1:8000/docs`.

## 🔌 API Usage

**Endpoint:** `POST /chat`

**Request:**
```json
{
  "question": "What are the rules regarding self-exclusion?"
}

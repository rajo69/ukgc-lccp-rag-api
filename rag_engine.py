import os
import json
#import nest_asyncio
from llama_index.core import (
    Document,
    VectorStoreIndex,
    Settings,
    StorageContext,
    load_index_from_storage
)
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.nvidia import NVIDIA
from llama_index.embeddings.nvidia import NVIDIAEmbedding

# Apply nest_asyncio to handle event loops in web servers
#nest_asyncio.apply()

PERSIST_DIR = "./storage"
DATA_FILE = "lccp_rag_dataset.json"

class UKGC_RAG:
    def __init__(self):
        self.index = None
        self.query_engine = None
        self._initialize_settings()

    def _initialize_settings(self):
        """Setup NVIDIA models."""
        # Ensure API key is present
        if not os.getenv("NVIDIA_API_KEY"):
            raise ValueError("NVIDIA_API_KEY environment variable is missing!")

        Settings.llm = NVIDIA(
            model="microsoft/phi-4-mini-instruct",
            temperature=0
        )
        Settings.embed_model = NVIDIAEmbedding(
            model="nvidia/nv-embedqa-e5-v5",
            truncate="END"
        )

    def load_or_create_index(self):
        """Loads index from disk or creates it from JSON."""
        if os.path.exists(PERSIST_DIR):
            print("Loading existing index from storage...")
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            self.index = load_index_from_storage(storage_context)
        else:
            print("Creating new index using NVIDIA Embeddings...")
            if not os.path.exists(DATA_FILE):
                raise FileNotFoundError(f"{DATA_FILE} not found. Please ensure the JSON dataset is present.")

            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            documents = []
            for entry in data:
                doc = Document(
                    text=entry["full_chunk_text"],
                    metadata=entry["metadata"],
                    excluded_llm_metadata_keys=["related_links", "condition_id", "part", "section"],
                    excluded_embed_metadata_keys=["related_links"]
                )
                documents.append(doc)

            self.index = VectorStoreIndex.from_documents(documents)
            self.index.storage_context.persist(persist_dir=PERSIST_DIR)
            print("✅ Index saved to ./storage")

        # Setup the Query Engine
        qa_prompt = PromptTemplate(
            "You are a strict Regulatory Assistant for the UK Gambling Commission.\n"
            "Context:\n{context_str}\n"
            "Instructions:\n"
            "1. Answer ONLY based on the context.\n"
            "2. Cite the specific Code/Condition numbers.\n"
            "Query: {query_str}\n"
            "Answer: "
        )
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=5, 
            text_qa_template=qa_prompt
        )

    def query(self, question: str):
        if not self.query_engine:
            raise RuntimeError("Index not loaded. Call load_or_create_index() first.")
        
        response = self.query_engine.query(question)
        
        # Format sources into a clean list of dictionaries for the API response
        sources = []
        seen = set()
        for node in response.source_nodes:
            name = node.metadata.get('condition_name', 'Unknown')
            if name not in seen:
                seen.add(name)
                sources.append({
                    "condition": name,
                    "context": f"{node.metadata.get('part', '')} > {node.metadata.get('subsection', '')}",
                    "links": node.metadata.get('related_links', [])
                })
        
        return {
            "answer": response.response,
            "sources": sources
        }
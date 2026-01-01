from __future__ import annotations

from pathlib import Path
from typing import cast

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama


def load_or_build_index(
    *,
    knowledge_dir: str | Path,
    persist_dir: str | Path,
    model_name: str,
    request_timeout: float = 60.0,
) -> VectorStoreIndex:
    knowledge_dir = Path(knowledge_dir)
    persist_dir = Path(persist_dir)

    llm = Ollama(model=model_name, request_timeout=request_timeout)
    embed_model = OllamaEmbedding(model_name=model_name)

    if not persist_dir.exists():
        if not knowledge_dir.exists():
            raise FileNotFoundError(f"Knowledge directory not found: {knowledge_dir}")

        print("Generating Index...")
        documents = SimpleDirectoryReader(str(knowledge_dir)).load_data()
        index = VectorStoreIndex.from_documents(documents, llm=llm, embed_model=embed_model)
        index.storage_context.persist(persist_dir=str(persist_dir))
        return index

    print("Loading Index...")
    storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
    index = load_index_from_storage(storage_context, llm=llm, embed_model=embed_model)
    return cast(VectorStoreIndex, index)

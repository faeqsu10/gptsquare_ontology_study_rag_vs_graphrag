import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

load_dotenv()

def setup_chromadb():
    """ChromaDB 클라이언트 설정"""
    client = chromadb.Client()
    
    # OpenAI 임베딩 함수 설정
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.environ.get("OPENAI_API_KEY"),
        model_name="text-embedding-3-small"
    )
    
    return client, openai_ef

if __name__ == "__main__":
    client, openai_ef = setup_chromadb()
    print(client)
    print(openai_ef)

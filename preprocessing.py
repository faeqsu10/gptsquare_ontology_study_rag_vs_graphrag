import pandas as pd
import os
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()


def chunk_text(text, max_chunk_size=500, overlap_size=50):
    """langchain을 사용하여 텍스트를 청크로 분할"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size,
        chunk_overlap=overlap_size,
        separators=["\n\n", "\n", ".", "!", "?", " "]
    )
    return splitter.split_text(text)


def setup_chromadb():
    """ChromaDB 클라이언트 설정"""
    # "chroma_db" 라는 이름의 폴더에 데이터베이스를 저장하도록 설정
    client = chromadb.PersistentClient(path="chroma_db")
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.environ.get("OPENAI_API_KEY"),
        model_name="text-embedding-3-small"
    )
    return client, openai_ef


def get_collection_stats(collection):
    """컬렉션 통계 정보 출력"""
    results = collection.get()
    
    total_docs = len(results['ids'])
    data_types = {}
    
    for metadata in results['metadatas']:
        data_type = metadata.get('data_type', 'unknown')
        data_types[data_type] = data_types.get(data_type, 0) + 1
    
    print(f"\n컬렉션: {collection.name}")
    print(f"총 문서 수: {total_docs}")
    print("데이터 타입별 분포:")
    for data_type, count in data_types.items():
        print(f"  {data_type}: {count}개")


def insert_to_chromadb(client, openai_ef, collection_name, documents, metadatas, ids):
    """ChromaDB에 데이터 삽입"""
    print(f"{collection_name} 컬렉션에 데이터 삽입 중...")
    
    # 기존 컬렉션 삭제 (있다면)
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass  # 컬렉션이 없으면 무시
    
    # 새 컬렉션 생성
    collection = client.create_collection(
        name=collection_name,
        embedding_function=openai_ef
    )
    
    # 데이터 삽입
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"{collection_name} 삽입 완료: {len(documents)}개 문서")
    return collection


def process_all_data(input_dir="data"):
    """
    모든 데이터 통합 처리
    """
    print("모든 데이터 통합 처리 중...")
    
    all_documents = []
    all_metadatas = []
    all_ids = []
    
    # 1. 마크다운 파일들 처리
    print("마크다운 파일들 처리 중...")
    files_config = {
        "식당정보.md": "restaurant_info",
        "직원.md": "employee_info", 
        "메뉴.md": "menu_info",
        "공급업체.md": "supplier_info"
    }
    
    for filename, data_type in files_config.items():
        try:
            with open(Path(input_dir) / filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            chunks = chunk_text(content, max_chunk_size=600, overlap_size=100)
            
            for i, chunk in enumerate(chunks):
                all_documents.append(chunk)
                all_metadatas.append({
                    "data_type": data_type,
                    "filename": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
                all_ids.append(f"{data_type}_{i}")
            
            print(f"{filename} 처리 완료: {len(chunks)}개 청크")
            
        except FileNotFoundError:
            print(f"{filename} 파일을 찾을 수 없습니다.")
            continue
    
    # 2. 구매이력 데이터 처리
    print("구매이력 데이터 처리 중...")
    try:
        df_purchase = pd.read_csv(Path(input_dir) / "csv_output" / "4데이터_구매이력.csv")
        print(f"총 {len(df_purchase)}개 구매 레코드 로드")
        
        for idx, row in df_purchase.iterrows():
            purchase_text = f"사용자 {row['User']}이 {row['Date']}에 {row['MenuItem']} {row['Quantity']}개를 {row['PricePerUnit']:,}원에 구매하여 총 {row['TotalPrice']:,}원을 지불했습니다."
            
            all_documents.append(purchase_text)
            all_metadatas.append({
                "data_type": "purchase",
                "user": row['User'],
                "menu_item": row['MenuItem'],
                "quantity": int(row['Quantity']),
                "price_per_unit": int(row['PricePerUnit']),
                "total_price": int(row['TotalPrice']),
                "date": row['Date']
            })
            all_ids.append(f"purchase_{idx}")
        
        print(f"구매이력 데이터 처리 완료: {len(df_purchase)}개 문서")
        
    except FileNotFoundError:
        print("구매이력 CSV 파일을 찾을 수 없습니다.")
    
    # 3. 리뷰 데이터 처리
    print("리뷰 데이터 처리 중...")
    try:
        df_review = pd.read_csv(Path(input_dir) / "csv_output" / "5데이터_리뷰.csv")
        print(f"총 {len(df_review)}개 리뷰 레코드 로드")
        
        for idx, row in df_review.iterrows():
            review_text = f"사용자 {row['User']}이 {row['Date']}에 평점 {row['Rating']}점으로 '{row['Review']}'라는 리뷰를 남겼습니다."
            
            all_documents.append(review_text)
            all_metadatas.append({
                "data_type": "review",
                "user": row['User'],
                "rating": int(row['Rating']),
                "review_text": row['Review'],
                "date": row['Date']
            })
            all_ids.append(f"review_{idx}")
        
        print(f"리뷰 데이터 처리 완료: {len(df_review)}개 문서")
        
    except FileNotFoundError:
        print("리뷰 CSV 파일을 찾을 수 없습니다.")
    
    print(f"전체 데이터 처리 완료: {len(all_documents)}개 문서")
    return all_documents, all_metadatas, all_ids


def main():
    """메인 실행 함수"""
    print("데이터 처리 및 벡터DB 로딩 시작\n")
    
    # ChromaDB 설정
    client, openai_ef = setup_chromadb()
    
    # 모든 데이터 통합 처리
    print("=" * 50)
    print("모든 데이터 통합 처리")
    print("=" * 50)
    all_docs, all_metas, all_ids = process_all_data()
    
    # 하나의 컬렉션에 저장
    unified_collection = insert_to_chromadb(
        client, openai_ef, "unified_data", 
        all_docs, all_metas, all_ids
    )
    get_collection_stats(unified_collection)
    
    print("\n모든 작업 완료!")
    print(f"통합 컬렉션: {unified_collection.count()}개 문서")


if __name__ == "__main__":
    
    main()




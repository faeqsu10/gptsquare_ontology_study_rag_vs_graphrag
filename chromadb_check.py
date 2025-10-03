import chromadb
import pprint
from collections import defaultdict

def inspect_collection_schema(db_path="chroma_db", collection_name="unified_data"):
    """
    ChromaDB 컬렉션의 데이터 구조를 분석하고 종류별로 필드와 예시를 출력합니다.
    """
    print(f"'{collection_name}' 컬렉션의 데이터 구조 분석을 시작합니다...\n")
    
    try:
        # 1. 디스크에 저장된 DB에 연결
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(name=collection_name)

        # 2. 컬렉션의 모든 데이터 가져오기
        results = collection.get(include=["metadatas", "documents"])
        
        # 3. 데이터 종류(data_type)별로 데이터 구조를 저장할 딕셔너리
        schema_by_type = defaultdict(lambda: {"fields": set(), "count": 0, "example": None})

        # 4. 모든 데이터를 순회하며 구조 분석
        for i, metadata in enumerate(results['metadatas']):
            data_type = metadata.get('data_type', 'unknown')
            
            # 해당 타입의 문서 개수 카운트
            schema_by_type[data_type]["count"] += 1
            
            # 해당 타입의 모든 메타데이터 필드 이름을 저장 (set이라 중복 없음)
            schema_by_type[data_type]["fields"].update(metadata.keys())
            
            # 각 타입의 첫 번째 데이터만 예시로 저장
            if schema_by_type[data_type]["example"] is None:
                schema_by_type[data_type]["example"] = {
                    "id": results['ids'][i],
                    "metadata": metadata,
                    "document": results['documents'][i]
                }

        # 5. 분석 결과 출력
        print("=" * 60)
        print("컬렉션 구조 분석 결과")
        print("=" * 60)
        
        for data_type, info in schema_by_type.items():
            print(f"\n데이터 타입: '{data_type}'")
            print(f"   - 총 문서 수: {info['count']}개")
            print(f"   - 메타데이터 필드: {sorted(list(info['fields']))}")
            
            print("\n   [대표 예시 데이터]")
            pprint.pprint(info['example'], indent=4, width=100)
            print("-" * 60)
            
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        print(f"'{db_path}' 폴더나 '{collection_name}' 컬렉션이 존재하는지 확인해주세요.")


# 스크립트 실행
if __name__ == "__main__":
    inspect_collection_schema()
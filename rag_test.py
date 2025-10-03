import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def query_chromadb(question, n_results=5):
    """ChromaDB에서 질문에 대한 답변 검색"""
    try:
        # ChromaDB 클라이언트 생성
        client = chromadb.PersistentClient(path="chroma_db")
        
        # OpenAI 임베딩 함수 설정 (컬렉션 생성 시와 동일한 함수 사용)
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.environ.get("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
        
        # 컬렉션 가져오기 (임베딩 함수 지정)
        collection = client.get_collection(
            name="unified_data",
            embedding_function=openai_ef
        )
        
        # print(f"질문: {question}")
        # print("="*50)
        
        # 벡터 검색 실행
        results = collection.query(
            query_texts=[question],
            n_results=n_results
        )
        
        # print(f"검색된 문서 수: {len(results['documents'][0])}")
        # print()
        
        # 결과 출력
        # for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        #     print(f"{i+1}. [{metadata['data_type']}] {doc}")
        #     print("\n\n")
        #     print(f"[메타데이터]: {metadata}")
        #     print("--------------------------------"*2)
        #     print("--------------------------------"*2)
        
        return results
        
    except Exception as e:
        print(f"검색 중 오류 발생: {e}")
        return None


def generate_answer_with_llm(question, search_results):
    """검색된 문서를 바탕으로 LLM이 답변 생성"""
    try:
        # OpenAI 클라이언트 초기화
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # 검색된 문서들을 context로 구성
        context_docs = search_results['documents'][0]
        context_metadatas = search_results['metadatas'][0]
        
        # Context 구성
        context = ""
        for i, (doc, metadata) in enumerate(zip(context_docs, context_metadatas)):
            context += f"[문서 {i+1} - {metadata['data_type']}]\n{doc}\n\n"
        
        # 프롬프트 구성
        prompt = f"""다음은 레스토랑 관련 데이터베이스에서 검색된 문서들입니다. 
이 정보를 바탕으로 사용자의 질문에 정확하고 도움이 되는 답변을 해주세요.

검색된 문서들:
{context}

사용자 질문: {question}

답변 시 주의사항:
- 검색된 문서의 정보만을 바탕으로 답변하세요
- 정보가 부족하거나 불확실한 경우 그렇게 명시하세요
- 구체적인 수치나 정보가 있다면 정확히 제시하세요
- 친근하고 도움이 되는 톤으로 답변하세요

답변:"""

        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "당신은 레스토랑 정보를 도와주는 친절한 AI 어시스턴트입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"LLM 답변 생성 중 오류 발생: {e}")
        return None
    

def rag_query(question, n_results=5):
    """RAG 시스템: 검색 + LLM 답변 생성"""
    print("관련 문서 검색 중...")
    search_results = query_chromadb(question, n_results)
    
    if search_results is None:
        print("문서 검색에 실패했습니다.")
        return None
    
    print("\nLLM이 답변을 생성 중...")
    answer = generate_answer_with_llm(question, search_results)
    
    if answer:
        print("\n" + "="*50)
        print("최종 답변:")
        print("="*50)
        print(answer)
        print("="*50)
    
    return answer

import concurrent.futures
import time
def rag_query_parallel(questions, n_results=5, max_workers=3):
    """여러 질문을 병렬로 처리하는 RAG 시스템"""
    print(f"{len(questions)}개 질문을 병렬로 처리 시작 (최대 {max_workers}개 동시 처리)")
    print(f"시작 시간: {time.strftime('%H:%M:%S')}")
    
    start_time = time.time()
    
    # ThreadPoolExecutor를 사용한 병렬 처리
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 각 질문에 대해 RAG 처리 작업 제출
        future_to_question = {
            executor.submit(rag_query, question, n_results): question 
            for question in questions
        }
        
        # 결과 수집
        results = {}
        for future in concurrent.futures.as_completed(future_to_question):
            question = future_to_question[future]
            try:
                answer = future.result()
                results[question] = answer
                print(f"'{question}' 처리 완료")
            except Exception as e:
                print(f"'{question}' 처리 중 오류: {e}")
                results[question] = None
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n모든 질문 처리 완료!")
    print(f"총 소요 시간: {total_time:.2f}초")
    print(f"평균 처리 시간: {total_time/len(questions):.2f}초/질문")
    
    return results


def test_queries():
    """다양한 질문 테스트"""
    
    questions = [
        "Bella Roma 레스토랑의 영업시간을 알려주세요.",
        "Bella Roma 전화번호는?",
        "Bella Roma 좌석 수는?",
        "김철수 주방장 정보는?",
        "마르게리타 피자 가격은?",
        "사용자1이 구매한 메뉴는?",
        "5점 리뷰는 어떤 것들이 있나요?",
        "티라미수에 대한 리뷰는?"
    ]
    
    for question in questions:
        print("\n" + "="*80)
        rag_query(question)
        print("\n" + "="*80)


def test_queries_parallel():
    """병렬 처리로 다양한 질문 테스트"""
    
    questions = [
        "Bella Roma 레스토랑의 영업시간을 알려주세요.",
        "Bella Roma의 전화번호는?",
        "Bella Roma의 좌석 수는?",
        "김철수 주방장 정보는?",
        "마르게리타 피자 가격은?",
        "사용자1이 구매한 메뉴는?",
        "5점 리뷰는 어떤 것들이 있나요?",
        "티라미수에 대한 리뷰는?"
    ]
    
    # 병렬 처리 실행
    results = rag_query_parallel(questions, n_results=3, max_workers=3)
    
    # 결과 요약
    print(f"\n처리 결과 요약:")
    print(f"{'='*60}")
    for question, answer in results.items():
        status = "성공" if answer else "실패"
        print(f"{status} | {question}")


if __name__ == "__main__":
    # 특정 질문 테스트
    # query_chromadb("Bella Roma 레스토랑의 영업시간을 알려주세요.")
    rag_query("Bella Roma의 전화번호, 영업시간, 좌석 수는?")
    
    # 병렬 질문 테스트
    # test_queries_parallel()
    
    
    # 또는 모든 질문 테스트
    # test_queries()
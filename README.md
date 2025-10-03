# 🍝 Bella Roma RAG vs GraphRAG 실습

> GPT Square 온톨로지 실습: 이탈리안 레스토랑 데이터를 활용한 RAG 시스템 비교 분석

## 📋 프로젝트 개요

서울 신촌의 이탈리안 레스토랑 'Bella Roma' 데이터를 활용하여 다양한 RAG 기법을 구현하고 비교하는 실습 프로젝트입니다.

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/faeqsu10/gptsquare_ontology_study_rag_vs_graphrag.git
cd gptsquare_ontology_study_rag_vs_graphrag
```

### 2. 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (.env 파일 생성)
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 실행
```bash
jupyter notebook
```

## 📚 노트북 실행 순서

1. **`1_excel_to_csv.ipynb`** - Excel 데이터를 CSV로 변환
2. **`2_data_analysis.ipynb`** - 데이터 탐색 및 분석
3. **`3_preprocessing.ipynb`** - 데이터 전처리 및 ChromaDB 저장
4. **`4_rag.ipynb`** - 기본 RAG 시스템 (ChromaDB)
5. **`5-1_graph_rag_test.ipynb`** - GraphRAG 테스트 (Neo4j)
6. **`6-1_hybrid_rag.ipynb`** - 하이브리드 RAG 시스템

## 📊 데이터 구성

- **메뉴**: 이탈리안 레스토랑 메뉴 정보
- **직원**: 직원 정보 및 역할
- **공급업체**: 식자재 공급업체 정보
- **구매이력**: 고객 구매 기록
- **리뷰**: 고객 리뷰 및 평점

## 🛠️ 주요 기술

- **RAG**: LangChain + ChromaDB + OpenAI
- **GraphRAG**: LangChain + Neo4j + OpenAI
- **하이브리드**: 벡터 검색 + 그래프 검색 결합

## 📁 프로젝트 구조

```
├── data/                    # 데이터 파일
│   ├── csv_output/         # CSV 변환된 데이터
│   └── *.md               # 마크다운 데이터
├── note/                   # 프로젝트 노트
├── chroma_db/             # ChromaDB 벡터 DB
├── *.ipynb                # Jupyter 노트북
└── requirements.txt       # 의존성 패키지
```

## 🔧 주요 기능

- **데이터 전처리**: Excel → CSV 변환, 텍스트 청크 분할
- **벡터 RAG**: 의미적 유사도 검색 기반 질의응답
- **그래프 RAG**: 관계 기반 추론 질의응답
- **하이브리드 RAG**: 다중 검색 결과 통합

## 📈 RAG 방식 비교

| 방식 | 장점 | 단점 |
|------|------|------|
| **벡터 RAG** | 유연한 쿼리, 의미적 검색 | 관계 정보 부족 |
| **GraphRAG** | 정확한 관계 추론 | 복잡한 설정 |
| **하이브리드** | 두 방식 장점 결합 | 복잡성 증가 |

## 🤝 스터디 참여자

- **faeqsu10**: 프로젝트 리드

---

**교육 목적 프로젝트** | [GitHub](https://github.com/faeqsu10/gptsquare_ontology_study_rag_vs_graphrag)

1.
온톨로지 구축 시, 노드끼리의 직접적인 관계를 설정하지 않으면(관계를 촘촘하게 구축하지 않을 경우), 사이퍼 쿼리 작성이 복잡해 진다 => 검색이 잘 안될 수 있음 (text-to-cypher 구축이 어려워짐)

메뉴와 카테고리 관계 추가 (질문7에 대한 쿼리 개선을 위해)
```
MATCH (m:MenuItem)
MATCH (mc:MenuCategory {name: m.category})
MERGE (m)-[:BELONGS_TO]->(mc);
```

- `(마르게리타 피자)` **-[:BELONGS_TO]->** `(피자)`
- `(까르보나라 파스타)` **-[:BELONGS_TO]->** `(파스타)`
- `(티라미수)` **-[:BELONGS_TO]->** `(디저트)`
- `(아메리카노)` **-[:BELONGS_TO]->** `(음료)`


2.
neo4j sandbox에서 예전에 만들어놨던 그래프db 서버가 없어짐 
sandbox에서 다시 만들어서 온톨로지 구축 쿼리 다시 넣음


3.
대량의 파일을 밀어 넣어야 할 때,
온라인 시트(구글 스프레드시트)로 공유하여 csv파일 load
구글 시트 - 설정 필수 항목 
1. 웹에 게시 
2. 공개 url 복사

LOAD CSV
1. 구매이력
```fold
LOAD CSV WITH HEADERS FROM 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRl4Cva8r2ipdfAp8X7H2P3dnmmgkUsXHOyTr8OQqZ3VSZW8dcLChGjbK2WXGAesgyw7kxfqU573ApX/pub?gid=371051440&single=true&output=csv' AS row
MATCH (u:Customer {id: row.User})
MATCH (m:MenuItem {name: row.MenuItem})
CREATE (p:Purchase {quantity: toInteger(row.Quantity), pricePerUnit: toInteger(row.PricePerUnit), totalPrice: toInteger(row.TotalPrice), purchaseDate: date(row.Date)})
CREATE (u)-[:MADE_PURCHASE]->(p)
CREATE (p)-[:FOR_MENU_ITEM]->(m);
```

2. 리뷰
```fold
LOAD CSV WITH HEADERS FROM 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRW9FefSzD2lt49id4tMkP3RP4RbPSNy3djTu4nMkygUeeQRXsrz_c3YzfVIRPwOhzGOrjhOdG92wYV/pub?gid=1816247089&single=true&output=csv' AS row
MATCH (c:Customer {id: row.User})
MATCH (r:Restaurant {name: 'Bella Roma'})
CREATE (rev:CustomerReview {
    rating: toInteger(row.Rating),
    text: row.Review,
    reviewDate: date(row.Date)
})
CREATE (c)-[:WROTE_REVIEW]->(rev)
CREATE (rev)-[:REVIEWS]->(r);
```

   
4.
티라미수 구매이력이 있는고객을 찾고
그 고객이 작성한 리뷰를 찾고
그 리뷰 정보를 반환
이 데이터는 111개 row 데이터
→ json or csv로 출력 해서 llm에게 던지는 식으로 해야할까?


5.
neo4j 쿼리해서 나온 결과 값도 넘겨 주어야 하지만,
온톨로지 구축 데이터 정보를 llm에게 참고하도록 넘겨주어야 할까? (llm이 삼중항 구조를 참고하므로써, 관계를 더욱 잘 파악 시키기 위해서)

6.
7번 질의에 대한 neo4j와 pandas 집계 결과가 다르게 나옴
neo4j에 데이터를 넣을 때, 문제가 생긴 것으로 예상 됨


7.
누락된 데이터가 있어서,
gemini 활용하여 누락된 데이터 추가

```Cypher
// Part 1 - 6. Ingredient 섹션 수정 (채소 누락분 추가)
// ... (생략)
MERGE (:Ingredient {name: '물'});
MERGE (:Ingredient {name: '우유'});
MERGE (:Ingredient {name: '올리브오일'});
MERGE (:Ingredient {name: '채소'}); // <--- 누락 노드 추가
```

```Cypher
LOAD CSV WITH HEADERS FROM 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRW9FefSzD2lt49id4tMkP3RP4RbPSNy3djTu4nMkygUeeQRXsrz_c3YzfVIRPwOhzGOrjhOdG92wYV/pub?gid=1816247089&single=true&output=csv' AS row
MATCH (c:Customer {id: row.User})
MATCH (r:Restaurant {name: 'Bella Roma'})

// MERGE를 사용하여 중복 리뷰 생성 방지.
// 작성자 ID (보조 속성), 리뷰 텍스트, 날짜를 기준으로 고유성을 판단
MERGE (rev:CustomerReview {
    reviewDate: date(row.Date),
    text: row.Review,
    // MERGE의 기준으로 사용하기 위해 작성자 ID를 속성으로 저장 (옵션)
    userId: row.User
})
ON CREATE SET
    rev.rating = toInteger(row.Rating)

// 관계 역시 MERGE를 사용하여 중복 연결 방지
MERGE (c)-[:WROTE_REVIEW]->(rev)
MERGE (rev)-[:REVIEWS]->(r);
```

8.
데이터 구축이 되어 있다는 사실 발견… (형조님)
어떻게 하지? 있는 데이터로 테스트 하면 되겠네?
그럼 rag 구축을 해보자

9.
데이터 분할 기준
구매이력 - 483행 
- 문장으로 변환 → 적정 청크 길이로 나눠서 분할 → 삽입

리뷰 - 121행
- 문장으로 변환 → 적정 청크 길이로 나눠서 분할 → 삽입
- 메타데이터에는 뭐를 넣으면 좋을까? 

---

10.
청크를 어떻게 넣을까? 에 대한 정의를 하느라 시간이 오래걸림
결국 - 그래프db와의 성능 평가가 목적이기 때문에, 가장 단순하게 한 행씩 넣기로 결정함!

11.
데이터_기본정보, 데이터_메뉴, 데이터_직원, 데이터_공급업체, 데이터_구매이력, 데이터_리뷰
=> 
LLM 에게 요청
벡터 db에 넣기 위하여 테이블로된 csv파일 → 마크다운 형식의 줄글로 변환 → 내용 청킹 → 벡터db 삽입

데이터_구매이력, 리뷰
=>
각 row → 자연어로 변환 → 벡터db 삽입(메타데이터 정리하여 삽입)


12.
벡터db와 그래프db비교를 테스트하기 위함이니 벡터db는 하나의 collection에서 데이터를 관리

13.
LangChain이 내부적으로 Neo4j 그래프 스키마와 LLM(대규모 언어 모델)을 활용하여 해당 질문을 Cypher 쿼리로 변환하고, 그 결과를 다시 자연어 답변으로 생성

→ 단순한 질문들은 결과 출력을 잘 하지만, 복합질문은 쿼리를 잘 못만드는 듯.. 

14.
LangChain이 Neo4j 그래프 데이터베이스에 연결하여 그래프 스키마(Graph Schema) 정보를 추출해줌
```python
from langchain_community.graphs import Neo4jGraph
graph = Neo4jGraph(url=URL, username=USERNAME, password=PASSWORD)
graph.schema
```

결과
```
Node properties:
Restaurant {name: STRING, address: STRING, phone: STRING, hoursWeekday: STRING, hoursWeekend: STRING, seats: INTEGER, reservationAvailable: BOOLEAN, category: STRING}
Employee {name: STRING, experienceYears: INTEGER, role: STRING, workingDays: STRING}
Supplier {name: STRING, phone: STRING}
Customer {name: STRING}
MenuItem {name: STRING, category: STRING, price: INTEGER, currency: STRING}
MenuCategory {name: STRING}
Ingredient {name: STRING}
Allergy {name: STRING}
PaymentMethod {name: STRING}
Purchase {purchaseDate: DATE, quantity: INTEGER, totalPrice: INTEGER, pricePerUnit: INTEGER, customer: STRING, menuItem: STRING, seq: INTEGER, caption: STRING}
CustomerReview {reviewDate: DATE, rating: INTEGER, text: STRING, seq: INTEGER, author: STRING, caption: STRING}
ReservationChannel {name: STRING}
Relationship properties:

The relationships:
(:Restaurant)-[:ACCEPTS_PAYMENT_METHOD]->(:PaymentMethod)
(:Restaurant)-[:ACCEPTS_RESERVATION_CHANNEL]->(:ReservationChannel)
(:Restaurant)-[:HAS_MENU_ITEM]->(:MenuItem)
(:Employee)-[:WORKS_AT_RESTAURANT]->(:Restaurant)
(:Supplier)-[:SUPPLIES_INGREDIENT]->(:Ingredient)
(:MenuItem)-[:CONTAINS_INGREDIENT]->(:Ingredient)
(:MenuItem)-[:IN_MENU_CATEGORY]->(:MenuCategory)
(:MenuItem)-[:MAY_TRIGGER_ALLERGY]->(:Allergy)
(:Purchase)-[:FOR_MENU_ITEM]->(:MenuItem)
(:Purchase)-[:BY_CUSTOMER]->(:Customer)
(:Purchase)-[:AT_RESTAURANT]->(:Restaurant)
(:CustomerReview)-[:REVIEWS_RESTAURANT]->(:Restaurant)
(:CustomerReview)-[:WRITTEN_BY]->(:Customer)
```

15.
gpt-4.1-mini: 실패
gpt-5-mini: 성공
thinking 모델 사용하면 복합질의 답변 성공 (주방장까지 잘 찾음을 확인)


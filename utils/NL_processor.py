import re

def classify_query_type(query: str) -> str:
    """
    검색어가 자연어인지 키워드인지 간단한 규칙 기반으로 판단합니다.
    """
    query = query.strip()

    # 1. 길이 기반 판단
    words = query.split()
    num_words = len(words)
    if num_words > 5: # 5단어 초과면 자연어일 가능성 높음
        return "natural_language"

    # 2. 불용어 및 조사/어미 패턴 확인 (한국어 기준)
    # 간단한 불용어 리스트와 문장 종결 어미, 조사 패턴
    stopwords_korean = ["은", "는", "이", "가", "을", "를", "에", "에서", "와", "과", "로", "으로", "도", "만", "좀", "요", "입니다", "있나요", "해주세요", "추천해주세요", "어떤", "무엇"]
    
    for sw in stopwords_korean:
        if sw in query:
            # 불용어가 포함되어 있으면 자연어일 가능성 높음 (단, 짧은 쿼리 예외 처리 필요)
            if num_words > 2: # 2단어 초과 쿼리에 불용어 포함 시 자연어
                return "natural_language"

    # 3. 질문/명령형 어미 확인 (더 명확한 자연어 신호)
    if re.search(r'(주세요|해줘|추천|있나|있나요|떤가|떤가요|을까|을까요|뭐야|뭘까|뭔가요)\s*$', query):
        return "natural_language"
    
    # 4. 명확한 키워드 패턴 (예: 브랜드 + 모델명)
    # 실제 시스템에서는 상품명 DB와 비교하여 판단할 수 있습니다.
    # 여기서는 간단히 '브랜드 + 모델명' 패턴을 가정
    if re.match(r'^(삼성|LG|애플|다이슨)\s+.*(TV|냉장고|폰|청소기|세탁기|에어컨)', query, re.IGNORECASE):
         if num_words <= 4: # 짧은 키워드 조합일 경우
             return "keyword"


    # 위 조건에 해당하지 않으면 기본적으로 키워드로 간주 (더 짧고 명료한 쿼리)
    return "keyword"
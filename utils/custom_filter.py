import re

def price_filter_with_custom(query):
    """사용자 의도 분석을 통한 필터링"""

    filter_dict = {}

    # 가격 필터링을 위한 정규표현식 패턴
    # 1) N만원 이상 | N만원 부터
    price_pattern = r'(\d+)만원\s*(이상|부터)'
    price_match = re.search(price_pattern, query)
    
    if price_match:
        # SALE_PRC 키가 없으면 생성
        if "SALE_PRC" not in filter_dict:
            filter_dict["SALE_PRC"] = {}
        # 만원 단위를 원 단위로 변환 (예: 120만원 -> 1200000원)
        filter_dict["SALE_PRC"]["$gte"] = int(price_match.group(1)) * 10000
    
    # 2) N만원 이하 | N만원 까지
    price_pattern_lte = r'(\d+)만원\s*(이하|까지)'
    price_match_lte = re.search(price_pattern_lte, query)
    
    if price_match_lte:
        if "SALE_PRC" not in filter_dict:
            filter_dict["SALE_PRC"] = {}
        filter_dict["SALE_PRC"]["$lte"] = int(price_match_lte.group(1)) * 10000

    # 3) N만원 대
    price_pattern_range = r'(\d+)만원\s*대'
    price_match_range = re.search(price_pattern_range, query)
    
    if price_match_range:
        if "SALE_PRC" not in filter_dict:
            filter_dict["SALE_PRC"] = {}
        base_price = int(price_match_range.group(1)) * 10000
        filter_dict["SALE_PRC"]["$gte"] = base_price
        filter_dict["SALE_PRC"]["$lt"] = base_price * 2

    return filter_dict

import re

PRICE_UNIT = {
    "일": 1,
    "이": 2,
    "삼": 3,
    "사": 4,
    "오": 5,
    "육": 6,
    "칠": 7,
    "팔": 8,
    "구": 9,
    "십": 10,
    "백": 100,
    "천": 1000,
    "만": 10000,
    "십만": 100000,
    "백만": 1000000
}

def price_info(price_match):
    base_price = 1
    text_price = 0
    # 숫자형 금액
    if (price_match.group(1)):
        base_price *= int(price_match.group(1))
    # 문자형 금액
    first_unit = base_price
    if (price_match.group(2) or price_match.group(3)):
        if (price_match.group(2)):
            first_unit *= PRICE_UNIT[price_match.group(2)]
        if (price_match.group(3)):
            if (len(price_match.group(3)) > 2):
                first_unit *= PRICE_UNIT[price_match.group(3)[0]]
                if (str(first_unit)[0] == 1):
                    first_unit *= PRICE_UNIT[price_match.group(3)[1]]
                else:
                    first_unit += PRICE_UNIT[price_match.group(3)[1]] + PRICE_UNIT[price_match.group(3)[2]]
            elif (len(price_match.group(3)) > 1):
                first_unit *= PRICE_UNIT[price_match.group(3)[0]]
                if (str(first_unit)[0] == 1):
                    first_unit *= PRICE_UNIT[price_match.group(3)[1]]
                else:
                    first_unit += PRICE_UNIT[price_match.group(3)[1]]
            else:
                first_unit *= PRICE_UNIT[price_match.group(3)]
    text_price += first_unit

    second_unit = 0
    if (price_match.group(4)):
        second_unit = int(price_match.group(4))
    if (price_match.group(5) or price_match.group(6)):
        if (price_match.group(5)):
                second_unit = PRICE_UNIT[price_match.group(5)]
        if (price_match.group(6)):
            if (len(price_match.group(6)) > 1):
                second_unit *= PRICE_UNIT[price_match.group(6)[0]]
                text_price += second_unit
                text_price *= PRICE_UNIT[price_match.group(6)[1]]
            else:
                second_unit *= PRICE_UNIT[price_match.group(6)]
    text_price += second_unit
        

    third_unit = 0
    if (price_match.group(7)):
        third_unit = int(price_match.group(7))
    if (price_match.group(8) or price_match.group(9)):
        if (price_match.group(8)):
                third_unit = PRICE_UNIT[price_match.group(8)]
        if (price_match.group(9)):
            if (len(price_match.group(9)) > 1):
                third_unit *= PRICE_UNIT[price_match.group(9)[0]]
                text_price += third_unit
                text_price *= PRICE_UNIT[price_match.group(9)[1]]
            else:
                third_unit *= PRICE_UNIT[price_match.group(9)]
    text_price += third_unit

    fourth_unit = 0
    if (price_match.group(10)):
        fourth_unit = int(price_match.group(10))
    if (price_match.group(11)):
        if (price_match.group(11)):
            fourth_unit = PRICE_UNIT[price_match.group(11)]
    text_price += fourth_unit
    
    base_price = text_price * 10000
    return base_price

def price_filter_with_custom(query):
    """사용자 의도 분석을 통한 필터링"""

    filter_dict = {}

    # 가격 필터링을 위한 정규표현식 패턴
    # 1) N만원 이상 | N만원 부터
    price_pattern = r'(\d*)([일이삼사오육칠팔구]*)([십백천만]*)(\d*)([일이삼사오육칠팔구]*)([십백천만]*)(\d*)([일이삼사오육칠팔구]*)([십백천만]*)(\d*)([일이삼사오육칠팔구]*)만원\s*(이상|부터|초과)'
    price_match = re.search(price_pattern, query)
    
    if price_match:
        # SALE_PRC 키가 없으면 생성
        if "SALE_PRC" not in filter_dict:
            filter_dict["SALE_PRC"] = {}
        # 만원 단위를 원 단위로 변환 (예: 120만원 -> 1200000원)
        base_price = price_info(price_match)
        if (base_price > 0):
            filter_dict["SALE_PRC"]["$gte"] = base_price
    
    # 2) N만원 이하 | N만원 까지
    price_pattern_lte = r'(\d*)([일이삼사오육칠팔구]*)([십백천만]*)(\d*)([일이삼사오육칠팔구]*)([십백천만]*)(\d*)([일이삼사오육칠팔구]*)([십백천만]*)(\d*)([일이삼사오육칠팔구]*)만원\s*(이하|까지)'
    price_match_lte = re.search(price_pattern_lte, query)
    
    if price_match_lte:
        if "SALE_PRC" not in filter_dict:
            filter_dict["SALE_PRC"] = {}
        base_price = price_info(price_match_lte)
        if (base_price > 0):
            filter_dict["SALE_PRC"]["$lte"] = base_price
    # 3) N만원 대
    price_pattern_range = r'(\d*)([일이삼사오육칠팔구]*)([십백천만]*)(\d*)([일이삼사오육칠팔구]*)([십백천만]*)(\d*)([일이삼사오육칠팔구]*)([십백천만]*)(\d*)([일이삼사오육칠팔구]*)만원\s*대'
    price_match_range = re.search(price_pattern_range, query)
    
    if price_match_range:
        if "SALE_PRC" not in filter_dict:
            filter_dict["SALE_PRC"] = {}
        base_price = price_info(price_match_range)
        if (base_price > 0):
            filter_dict["SALE_PRC"]["$gte"] = base_price
            # (N만원 + 최대 자릿수)까지
            # 240만원: 240만원 ~ 340만원
            filter_dict["SALE_PRC"]["$lt"] = base_price + (10 ** (len(str(base_price)) - 1))

    return filter_dict

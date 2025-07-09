import re

def calculate_rank_score(metadata: dict, top_k:int) -> float:
    """
    랭킹 점수 계산 함수. 최대 3점
    top_k 가 100 일 때, 1위는 3.0점 100위는 0.03점
    """
    top_score = 3
    score = (top_k - metadata.get('similarity_rank') + 1) * top_score / top_k
    return float(int(score * 10) / 10)  # 소수점 첫째자리까지, 둘째자리 버림

def calculate_default_score(metadata: dict) -> float:
    """디폴트 점수 계산 함수. 최대 5점"""
    score = 0.0

    if metadata.get('GOODS_STAT_SCT_NM') == '정상상품':
        score += 1.0

    return score
    
def calculate_brand_score(metadata: dict, brand: str, artc: str) -> float:
    """브랜드 매칭 점수 계산 함수. 최대 5점"""
    score = 0.0

    # 브랜드 의도가 없는 경우
    if not brand:
        # 1. 기본 대표 브랜드
        FLAGSHIP_BRANDS = ['삼성전자', 'LG전자', 'Apple', 'PLUX']
        if metadata.get('BRND_NM', '') in FLAGSHIP_BRANDS:
            score += 2.0

        # 2. PB 추가 점수
        if metadata.get('BRND_NM', '') == 'PLUX':
            score += 1.0
    
        # 3. 품목별 대표 브랜드
        if artc == '커피머신':
            FLAGSHIP_PRODUCT_커피머신 = ['네스프레소', '카누']
            if any(flagship in metadata.get('BRND_NM', '') for flagship in FLAGSHIP_PRODUCT_커피머신):
                score += 1.0
        elif artc == '선풍기':
            FLAGSHIP_PRODUCT_커피머신 = ['신일', '루메나']
            if any(flagship in metadata.get('BRND_NM', '') for flagship in FLAGSHIP_PRODUCT_커피머신):
                score += 1.0

        return score
    
    # 브랜드 의도가 있을 경우

    # TODO: 브랜드명 그룹으로 확장. 예) 대표: 삼성 -> 삼성전자, 삼성전자(주)
    brands = []
    brands.append(brand)

    for b in brands:
        if b in metadata.get('BRND_NM', ''):
            score += 5.0  # 증가: 브랜드 정확 매칭 더 중요하게
        elif b in metadata.get('GOODS_NM', ''):
            score += 2.0  # 증가: 상품명 매칭도 중요도 상승

    return score

def calculate_artc_score(metadata: dict, artc:str) -> float:
    """품목 매칭 점수 계산 함수. 최대 4점"""
    score = 0.0
    if not artc:
        return score
    
    if metadata.get("SERVICE_YN") == 'Y':
        return score
    
    # 대표적인 상품
    if artc == '이어폰':
        FLAGSHIP_PRODUCT_이어폰 = ['갤럭시', '에어팟']
        if any(flagship in metadata.get('GOODS_NM', '') for flagship in FLAGSHIP_PRODUCT_이어폰):
            score += 1.0
    elif artc == '냉장고':
        FLAGSHIP_PRODUCT_냉장고 = ['비스포크 ', '오브제컬렉션']
        if any(flagship in metadata.get('GOODS_NM', '') for flagship in FLAGSHIP_PRODUCT_냉장고):
            score += 1.0
    elif artc == '에어컨':
        FLAGSHIP_PRODUCT_에어컨 = ['휘센 ', '무풍클래식']
        if any(flagship in metadata.get('GOODS_NM', '') for flagship in FLAGSHIP_PRODUCT_에어컨):
            score += 1.0
    
    # 품목매칭인 경우
    if artc in metadata.get('ARTC_NM', '').replace('일반', ''):
        score += 2.0

    # 품목이 카테고리에 있는 경우
    if artc in metadata.get('SGRP_NM', '').replace('일반', '').split('·'):
        score += 2.0  # 증가: 소카테고리 매칭 더 중요하게
    elif artc in metadata.get('MGRP_NM', '').replace('일반', '').split('·'):
        score += 1.5  # 증가: 중카테고리 매칭
    elif artc in metadata.get('LGRP_NM', '').replace('일반', '').split('·'):
        score += 1.0  # 증가: 대카테고리 매칭

    return score

def calculate_hashtag_score(metadata: dict, artc:str, features:list[str]) -> float:
    """해시태그 매칭 점수 계산 함수. 해시태그 1개당 1.5점"""
    score = 0.0

    if not artc and not features:
        return score

    # 품목이 관련키워드에 있을 경우
    # if artc and artc in metadata.get('SCH_KWD_NM', ''):
    #     score += 1.0

    # 특징이 관련키워드에 있을 경우
    for feature in features:
        if feature in metadata.get('SCH_KWD_NM', '').split('#'):
            score += 1.5

    return score

def calculate_features_score(metadata: dict, features:list[str]) -> float:
    """특징 매칭 점수 계산 함수. 특징 1개 당 3.5점"""
    score = 0.0

    # 특징이 상품명이나 주요 특징 및 기능에 있을 경우
    for feature in features:
        if feature in metadata.get('FEATURES', ''):
            score += 2.5
        elif feature in metadata.get('GOODS_NM', ''):
            score += 2.5

    return score

def calculate_cards_score(metadata: dict, cardDcNms:list[str]) -> float:
    """카드할인 매칭 점수 계산 함수. 카드 1개당 10점"""
    score = 0.0

    card_dc_nm_list = []
    if cardDcNms:
        card_dc_nm_list = cardDcNms

    # 원하는 할인카드가 할인카드 목록에 있는 경우
    for card_dc_nm in card_dc_nm_list:
        if card_dc_nm in metadata.get('CARD_DC_NAME_LIST', ''):
            score += 10
            # print(f"Hit CARD_DC_NAME_LIST: {feature}")

    return score

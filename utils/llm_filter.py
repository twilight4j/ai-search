import re

def price_filter_with_llm(intent):
    """가격 필터"""
    filter_dict = {}
    is_filter = False
    if "DSCNT_SALE_PRC" not in filter_dict:
        filter_dict["DSCNT_SALE_PRC"] = {}
    
    if intent["PRICE_GTE"] > 0:
        filter_dict["DSCNT_SALE_PRC"]["$gte"] = intent["PRICE_GTE"]
        is_filter = True
    if intent["PRICE_LTE"] > 0:
        filter_dict["DSCNT_SALE_PRC"]["$lte"] = intent["PRICE_LTE"]
        is_filter = True

    if not is_filter:
        return {}
    
    return filter_dict

def brand_filter_with_llm(intent):
    """브랜드 필터"""
    return {"BRND_NM": intent["BRND_NM"]}

def artc_filter_with_llm(intent):
    """품목 필터"""
    return  {"ARTC_NM": intent["ARTC_NM"]}

def category_filter_with_llm(intent):
    """카테고리 필터"""
    filter_dict = {}

    # 대카테고리
    lgrp_nm = intent.get("LGRP_NM")

    # 찾는 상품이 무형의 서비스라면, 대카테고리 다시 세팅
    if intent.get("SERVICE_YN") == 'Y':
        lgrp_nm = ['안심케어', '방문컨설팅']
    
    if lgrp_nm:
        # 여러 카테고리 중 하나라도 일치하면 통과하는 필터
        filter_dict = {"LGRP_NM": {"$in": lgrp_nm}}    

    return filter_dict

def features_filter_with_llm(intent):
    """주요기능 필터"""
    return  {"FEATURES": intent["FEATURES"]}

def review_point_filter_with_llm(intent):
    """리뷰점수 필터"""
    filter_dict = {}
    is_filter = False
    if "GDAS_SCR_SUM" not in filter_dict:
        filter_dict["GDAS_SCR_SUM"] = {}
    
    if intent["REVIEW_GTE"] > 0:
        filter_dict["GDAS_SCR_SUM"]["$gte"] = intent["REVIEW_GTE"]
        is_filter = True
    if intent["REVIEW_LTE"] > 0:
        filter_dict["GDAS_SCR_SUM"]["$lte"] = intent["REVIEW_LTE"]
        is_filter = True

    if not is_filter:
        return {}
    
    return filter_dict


import re

def price_filter_with_llm(intent):
    """가격 필터"""
    filter_dict = {}
    is_filter = False
    if "PRICE" not in filter_dict:
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
    # LGRP_NM이 리스트인지 확인
    lgrp_nm = intent.get("LGRP_NM")
    if isinstance(lgrp_nm, list):
        # 여러 카테고리 중 하나라도 일치하면 통과하는 필터
        filter_dict = {"LGRP_NM": {"$in": lgrp_nm}}
    elif lgrp_nm is not None:
        # 단일 값일 때
        filter_dict = {"LGRP_NM": lgrp_nm}
    else:
        # 값이 없을 때
        filter_dict = {}
    return filter_dict

def features_filter_with_llm(intent):
    """주요기능 필터"""
    return  {"FEATURES": intent["FEATURES"]}
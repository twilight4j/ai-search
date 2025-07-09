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
    if lgrp_nm:
        filter_dict = {"LGRP_NM": {"$in": lgrp_nm}}    

    # 중카테고리
    mgrp_nm = intent.get("MGRP_NM")
    if mgrp_nm:
        filter_dict = {"MGRP_NM": {"$in": mgrp_nm}}    

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


import re

def price_filter_with_llm(query, intent):
    filter_dict = {}
    # 가격
    if '가격' in query or '저렴' in query:
        if "SALE_PRC" not in filter_dict:
            filter_dict["SALE_PRC"] = {}
        filter_dict["SALE_PRC"]["$gte"] = intent["SALE_PRC_GTE"]
        filter_dict["SALE_PRC"]["$lte"] = intent["SALE_PRC_LTE"]
    return filter_dict

def brand_filter_with_llm(query, intent):
    filter_dict = {}
    # 브랜드
    filter_dict["BRND_NM"] = intent["BRND_NM"]
    return filter_dict

def artc_filter_with_llm(query, intent):
    filter_dict = {}
    # 품목
    filter_dict["ARTC_NM"] = intent["ARTC_NM"]
    return filter_dict

def category_filter_with_llm(query, intent):
    filter_dict = {}
    # 카테고리
    filter_dict["LGRP_NM"] = intent["LGRP_NM"]
    return filter_dict

def features_filter_with_llm(query, intent):
    filter_dict = {}
    # 주요 기능 및 특징
    filter_dict["FEATURES"] = intent["FEATURES"]
    return filter_dict
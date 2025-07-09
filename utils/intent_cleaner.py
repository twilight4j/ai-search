import re
from typing import Dict

def get_cleaned_intent(intent:Dict, query:str):

    # 카테고리 정제    
    intent['LGRP_NM'], intent['MGRP_NM'] = _clean_category_intent(intent, query)

    # FEATURES 정제
    cleaned_features = []
    features = intent.get('FEATURES')

    if features:
        for feature in features:
            cleaned_features.append(_clean_feature_size(feature.replace(' ', '')))

        intent['FEATURES'] = cleaned_features

    return intent

def _clean_feature_size(text):
    """
    텍스트 내에서 '램 {숫자}기가', '램{숫자} 기가', '16GB램' 등의 패턴을 '{숫자}GB'로 변경합니다.

    Args:
        text (str): 변경할 원본 텍스트.

    Returns:
        str: 변경된 텍스트.
    """
    # 기존 패턴: '램 16기가', '용량 16기가', '하드 16기가', '램16기가', ...
    text = re.sub(r'(?:램|용량|하드)\s*(\d+)\s*(?:기가|GB)', r'\1GB', text)
    # 추가 패턴: '16GB램', '16기가램', ...
    text = re.sub(r'(\d+)\s*(?:GB|기가)\s*램', r'\1GB', text)
    
    return text

def _clean_category_intent(intent, query):
    
    cleaned_lgrp_nms = []
    cleaned_mgrp_nms = []

    lgrp_nms = intent.get("LGRP_NM")
    mgrp_nms = intent.get("MGRP_NM")

    # 휴대폰·스마트워치
    if '휴대폰·스마트워치' in lgrp_nms:
        if '자급제' in query:
            cleaned_lgrp_nms.append('휴대폰·스마트워치')
            cleaned_mgrp_nms.append('자급제')
        elif 'SKT' in query:
            cleaned_lgrp_nms.append('휴대폰·스마트워치')
            cleaned_mgrp_nms.append('SKT')
        elif 'KT' in query:
            cleaned_lgrp_nms.append('휴대폰·스마트워치')
            cleaned_mgrp_nms.append('KT')
        elif 'LG' in query:
            cleaned_lgrp_nms.append('휴대폰·스마트워치')
            cleaned_mgrp_nms.append('LG')

    # 안심케어
    if intent.get("SERVICE_YN") == 'Y':
        cleaned_lgrp_nms.append('안심케어')
        cleaned_lgrp_nms.append('방문컨설팅')

    if cleaned_lgrp_nms:
        return cleaned_lgrp_nms, cleaned_mgrp_nms
    else:
        return lgrp_nms, mgrp_nms


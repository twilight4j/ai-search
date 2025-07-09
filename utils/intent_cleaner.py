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
    텍스트 내에서 '램 {숫자}기가' 또는 '램{숫자} 기가' 등의 패턴을 '{숫자}GB'로 변경합니다.

    Args:
        text (str): 변경할 원본 텍스트.

    Returns:
        str: 변경된 텍스트.
    """
    # 정규식 패턴 설명:
    # r'(?:램|용량)\s*(\d+)\s*기가'
    # (?:램|용량): '램' 또는 '용량' 중 하나에 매칭되지만, 이 부분을 캡처 그룹으로 저장하지는 않습니다 (?:...).
    # \s*: 앞 단어와 숫자 사이에 0개 이상의 공백.
    # (\d+): 하나 이상의 숫자에 매칭되고 캡처 그룹 1로 저장됩니다. 이 숫자가 RAM 용량이 됩니다.
    # \s*: 숫자와 '기가' 사이에 0개 이상의 공백.
    # 기가|GB: '기가' 또는 'GB' 문자열.

    # 대체 문자열:
    # r'\1GB'
    # \1: 캡처 그룹 1의 내용(즉, 숫자의 값)을 참조합니다.
    # GB: 고정 문자 'GB'를 추가합니다.
    return re.sub(r'(?:램|용량|하드)\s*(\d+)\s*(?:기가|GB)', r'\1GB', text)

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

    if cleaned_lgrp_nms and cleaned_mgrp_nms:
        return cleaned_lgrp_nms, cleaned_mgrp_nms
    else:
        return lgrp_nms, mgrp_nms


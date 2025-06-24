from utils.custom_filter import price_filter_with_custom
from utils.llm_filter import price_filter_with_llm
from utils.llm_filter import brand_filter_with_llm
from utils.llm_filter import category_filter_with_llm
from utils.llm_filter import artc_filter_with_llm
from utils.llm_filter import features_filter_with_llm

class FilterService:
    @staticmethod

    # 의도 기반 필터링 함수 선언
    def intent_based_filtering(query, intent):
        """사용자 의도 분석을 통한 필터링"""

        filter_dict = {}

        # 가격 필터
        filter_dict.update(price_filter_with_custom(query) or price_filter_with_llm(query, intent))

        # 브랜드 필터
        # filter_dict.update(brand_filter_with_llm(query, intent))

        # 카테고리 필터
        # filter_dict.update(category_filter_with_llm(query, intent))

        # 품목 필터
        # filter_dict.update(artc_filter_with_llm(query, intent))

        # 주요 기능 및 특징 필터
        # filter_dict.update(features_filter_with_llm(query, intent))

        return filter_dict

    
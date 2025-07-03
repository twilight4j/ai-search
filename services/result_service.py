from typing import List, Dict, Any
from langchain.schema import Document
from models.response import ProductResponse, IntentResponse, FilterResponse

class ResultService:
    @staticmethod
    def convert_to_products(results: List[Document]) -> List[ProductResponse]:
        """
        검색 결과(Document)를 products 형식으로 변환합니다.
        """
        products = []
        for doc in results:

            product = ProductResponse(
                goodsNo=doc.metadata.get("GOODS_NO", "unknown"),
                goodsStatSctNm=doc.metadata.get("GOODS_STAT_SCT_NM", "unknown"),
                brndNm=doc.metadata.get("BRND_NM", "unknown"),
                goodsNm=doc.metadata.get("GOODS_NM", "unknown"),
                artcNm=doc.metadata.get("ARTC_NM", "unknown"),
                categoryNm=doc.metadata.get("LGRP_NM", "unknown"),
                salePrc=int(doc.metadata.get("SALE_PRC", 0)),
                dscntSalePrc=int(doc.metadata.get("DSCNT_SALE_PRC", 0)),
                maxBenefitPrice=int(doc.metadata.get("MAX_BENEFIT_PRICE", 0)),
                cardDcRate=int(doc.metadata.get("CARD_DC_RATE", 0)),
                cardDcNameList=doc.metadata.get("CARD_DC_NAME_LIST", "unknown"),
                features=doc.metadata.get("FEATURES", "unknown"),
                schKwdNm=doc.metadata.get("SCH_KWD_NM", "unknown"),
                saleQty=int(doc.metadata.get("SALE_QTY", 0)),
                salesUnit=int(doc.metadata.get("SALES_UNIT", 0)),
                gdasScrSum=float(doc.metadata.get("GDAS_SCR_SUM", 0)),
                gdasCnt=int(doc.metadata.get("GDAS_CNT", 0)),
                energeyGrade=doc.metadata.get("ENERGEY_GRADE", "unknown"),
                mdlLnchDt=doc.metadata.get("MDL_LNCH_DT", "unknown"),
                similarity_score=float(doc.metadata.get("similarity_score", 0.0)),
                weight=float(doc.metadata.get("weight", 0.0)),
                weight_analysis=doc.metadata.get("weight_analysis", "unknown"),
                content=doc.page_content
            )
            products.append(product)
        return products 
    
    @staticmethod
    def convert_to_intent_response(intent: dict) -> IntentResponse:
        """
        예시
            {
                'INTENTED_QUERY': '방수 기능과 노이즈 캔슬링이 있는 이어폰', 
                'PRICE_GTE': 200000, 
                'PRICE_LTE': 299999, 
                'BRND_NM': '', 
                'ARTC_NM': '이어폰', 
                'LGRP_NM': ['음향가전'], 
                'FEATURES': '방수, 노이즈캔슬링', 
                'CARD_DC_NMS': ['롯데카드'], 
                'REVIEW_GTE': 0.0, 
                'REVIEW_LTE': 0.0
            }
        결과
            {
                "intentedQuery": "방수 기능과 노이즈 캔슬링이 있는 이어폰",
                "price": "200,000원 이상 299,999원 이하",
                "brndNm": "",
                "artcNm": "이어폰",
                "lgrpNm": "음향가전",
                "features": "방수, 노이즈캔슬링",
                "cardDcNm": "롯데카드",
                "review": ""
            }
        """
        # 가격
        price:str = ''
        priceGte = intent.get('PRICE_GTE', 0)
        priceLte = intent.get('PRICE_LTE', 0)
        if priceGte:
            price += f"{priceGte:,}원 이상"
        if priceLte:
            if price:
                price += " "
            price += f"{priceLte:,}원 이하"

        # 카테고리
        lgrpNm:str = ''
        lgrpNm_list = intent.get('LGRP_NM')
        if lgrpNm_list:
            lgrpNm = ', '.join(lgrpNm_list)

        # 할인카드
        cardDcNm:str = ''
        cardDcNm_list = intent.get('CARD_DC_NMS')
        if cardDcNm_list:
            cardDcNm = ', '.join(cardDcNm_list)

        # 리뷰
        review:str = ''
        reviewGte = intent.get('REVIEW_GTE', 0)
        reviewLte = intent.get('REVIEW_LTE', 0)
        if reviewGte:
            review += f"{reviewGte}점 이상"
        if reviewLte:
            if review:
                review += " "
            review += f"{reviewLte}점 이하"

        # 기타
        etc:str = ''
        if intent.get('SERVICE_YN', 'N') == 'Y':
            etc += f"안심케어 서비스"

        intent_response = IntentResponse(
            intentedQuery=intent.get('INTENTED_QUERY', ''),
            price=price,
            brndNm=intent.get('BRND_NM', ''),
            artcNm=intent.get('ARTC_NM', ''),
            lgrpNm=lgrpNm,
            features=intent.get('FEATURES', ''),
            cardDcNm=cardDcNm,
            review=review,
            etc=etc
        )
        return intent_response
    
    @staticmethod
    def convert_to_filter_response(filter_dict: dict) -> FilterResponse:
        """
        예시
            {
                'DSCNT_SALE_PRC': {
                    '$gte': 200000, 
                    '$lte': 299999
                }, 
                'LGRP_NM': {
                    '$in': ['음향가전']
                }
            }
        결과
            {
                "dscntSalePrc": "200,000원 이상 299,999원 이하",
                "lgrpNm": "음향가전",
                "review": ""
            },
        """
        # 가격필터
        dscntSalePrc:str = ''
        if filter_dict.get('DSCNT_SALE_PRC'):
            dscntSalePrcGte = filter_dict.get('DSCNT_SALE_PRC').get('$gte')
            dscntSalePrcLte = filter_dict.get('DSCNT_SALE_PRC').get('$lte')
            if dscntSalePrcGte:
                dscntSalePrc += f"{dscntSalePrcGte:,}원 이상"
            if dscntSalePrcLte:
                if dscntSalePrc:
                    dscntSalePrc += " "
                dscntSalePrc += f"{dscntSalePrcLte:,}원 이하"

        # 카테고리필터
        lgrpNm:str = ''
        if filter_dict.get('LGRP_NM'): 
            lgrpNm_list = filter_dict.get('LGRP_NM').get('$in')
            if lgrpNm_list:
                lgrpNm = ', '.join(lgrpNm_list)

        # 리뷰필터
        review:str = ''
        if filter_dict.get('GDAS_SCR_SUM'):
            reviewGte = filter_dict.get('GDAS_SCR_SUM').get('$gte')
            reviewLte = filter_dict.get('GDAS_SCR_SUM').get('$lte')
            if reviewGte:
                review += f"{reviewGte}점 이상"
            if reviewLte:
                if review:
                    review += " "
                review += f"{reviewLte}점 이하"

        filter_response = FilterResponse(
            dscntSalePrc=dscntSalePrc,
            lgrpNm=lgrpNm,
            review=review,
        )
        return filter_response
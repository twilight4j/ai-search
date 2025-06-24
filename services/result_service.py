from typing import List, Dict, Any
from langchain.schema import Document
from models.response import ProductResponse

class ResultService:
    @staticmethod
    def convert_to_products(results: List[Document]) -> List[ProductResponse]:
        """
        검색 결과(Document)를 products 형식으로 변환합니다.
        """
        products = []
        for doc in results:
            
            # feature 옵션이름과 값을 매핑하여 최대 3개까지만 생성
            feature = ''
            feature_values = doc.metadata.get("OPT_VAL_DESC", "").split(',')
            feature_titles = doc.metadata.get("OPT_DISP_NM", "").split(',')
            for i, (title, value) in enumerate(zip(feature_titles, feature_values)):
                feature = f" - {title} : {value}"
                if i == 2: break

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
                featureInfo=feature,
                schKwdNm=doc.metadata.get("SCH_KWD_NM", "unknown"),
                saleQty=int(doc.metadata.get("SALE_QTY", 0)),
                salesUnit=int(doc.metadata.get("SALES_UNIT", 0)),
                gdasScrSum=float(doc.metadata.get("GDAS_SCR_SUM", 0)),
                gdasCnt=int(doc.metadata.get("GDAS_CNT", 0)),
                energeyGrade=doc.metadata.get("ENERGEY_GRADE", "unknown"),
                mdlLnchDt=doc.metadata.get("MDL_LNCH_DT", "unknown"),
                similarity_score=float(doc.metadata.get("similarity_score", 0.0)),
                similarity_rank=int(doc.metadata.get("similarity_rank", 9999)),
                content=doc.page_content
            )
            products.append(product)
        return products 
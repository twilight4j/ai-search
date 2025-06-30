import logging
from typing import List, Dict, Any, Tuple, Union
from langchain.schema import Document
from utils.score_calculator import calculate_artc_score
from utils.score_calculator import calculate_brand_score
from utils.score_calculator import calculate_features_score
from utils.score_calculator import calculate_hashtag_score
from utils.score_calculator import calculate_rank_score
from utils.score_calculator import calculate_cards_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SortService:
    @staticmethod
    def sort_products(docs: List[Union[Document, Tuple[Document, float]]], top_k:int, intent:Dict) -> List[Document]:
        """
        검색 결과를 정렬 기준에 따라 정렬합니다.
        정렬 기준:
        1) SALE_STAT_CD / ASC /* 01 판매중 02 품절 */
        2) GOODS_STAT_SCT_CD !='03'/ DESC /* 03 진열상품 */
        3) APPLIANCES_YN = 'Y' / DESC
        4) weight / DESC
        5) SALES_UNIT / DESC
        6) SALE_QTY / DESC
        7) GOODS_TP_CD IN ('05', '10') / DESC /* 05 렌탈상품 10 상담상품 */
        8) GOODS_STAT_SCT_CD / ASC
        9) GOODS_NO / DESC

        가중치(weight) 모델
        1) 순위점수(similarity_rank)
        2) 브랜드(BRND_NM)
        3) 품목(ARTC_NM)
        4) 특징(FEATURES)
        5) 할인카드(CARD_DC_NAME_LIST)
        """

        # 튜플 형태의 결과를 Document로 변환
        processed_docs = []
        for i, item in enumerate(docs):
            if isinstance(item, tuple):
                doc, score = item
                doc.metadata['similarity_score'] = score
            else:
                doc = item
                doc.metadata['similarity_score'] = 0.0
            doc.metadata['similarity_rank'] = i + 1
            processed_docs.append(doc)

        def get_sort_key(doc: Document) -> tuple:
            metadata = doc.metadata


            # SALE_STAT_CD / ASC
            sale_stat_cd = metadata.get('SALE_STAT_CD', '')
            
            # GOODS_STAT_SCT_CD !='03'/ DESC
            stat_sct_cd = metadata.get('GOODS_STAT_SCT_CD', '')
            stat_sct_cd_is_not_03 = 1 if stat_sct_cd != '03' else 0
            
            # APPLIANCES_YN = 'Y' / DESC
            appliances_yn = metadata.get('APPLIANCES_YN', '')
            is_appliance = 1 if appliances_yn == 'Y' else 0
            
            # 가중치(weight) / DESC
            # rank_score = calculate_rank_score(metadata, top_k)
            # brand_score = calculate_brand_score(metadata, intent.get('BRND_NM'))
            # artc_score = calculate_artc_score(metadata, intent.get('ARTC_NM'))
            # hashtag_score = calculate_hashtag_score(metadata, intent.get('ARTC_NM'), intent.get('FEATURES'))
            # features_score = calculate_features_score(metadata, intent.get('FEATURES'))

            # weight = rank_score + brand_score + artc_score + hashtag_score + features_score
            # metadata['weight'] = weight
            # metadata['weight_analysis'] = f"랭킹:{rank_score}, 브랜드:{brand_score}, 품목:{artc_score}, 해시태그:{hashtag_score}, 특징:{features_score}"

            scores:list[float] = [
                calculate_rank_score(metadata, top_k),
                calculate_brand_score(metadata, intent.get('BRND_NM')),
                calculate_artc_score(metadata, intent.get('ARTC_NM')),
                calculate_hashtag_score(metadata, intent.get('ARTC_NM'), intent.get('FEATURES')),
                calculate_features_score(metadata, intent.get('FEATURES')),
                calculate_cards_score(metadata, intent.get('CARD_DC_NMS'))
            ]
            weight = sum(scores)
            metadata['weight'] = weight
            metadata['weight_analysis'] = f"랭킹:{scores[0]}, 브랜드:{scores[1]}, 품목:{scores[2]}, 해시태그:{scores[3]}, 특징:{scores[4]}, 할인카드:{scores[5]}"

            # SALES_UNIT 외부판매량 / DESC
            sales_unit = int(metadata.get('SALES_UNIT', 0))

            # SALE_QTY 자사판매량 / DESC
            sale_qty = int(metadata.get('SALE_QTY', 0))
            
            # GOODS_TP_CD IN ('05', '10') / DESC
            goods_tp_cd = metadata.get('GOODS_TP_CD', '')
            is_target_type = 1 if goods_tp_cd in ('05', '10') else 0        
            
            # GOODS_NO / DESC
            goods_no = metadata.get('GOODS_NO', '')
            
            return (
                sale_stat_cd, # ASC
                -stat_sct_cd_is_not_03,  # DESC
                -is_appliance,  # DESC
                -weight,  # DESC
                -sales_unit, # DESC
                -sale_qty, # DESC
                -is_target_type,  # DESC
                stat_sct_cd,  # ASC
                -int(goods_no) if goods_no.isdigit() else goods_no  # DESC
            )
        
        return sorted(processed_docs, key=get_sort_key)
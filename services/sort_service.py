from typing import List, Dict, Any, Tuple, Union
from langchain.schema import Document

class SortService:
    @staticmethod
    def sort_products(docs: List[Union[Document, Tuple[Document, float]]]) -> List[Document]:
        """
        검색 결과를 정렬 기준에 따라 정렬합니다.
        정렬 기준:
        1) GOODS_STAT_SCT_CD !='03'/ DESC
        2) APPLIANCES_YN = 'Y' / DESC
        3) similarity_rank / ASC (문서 순서 기반 랭크)
        4) GOODS_TP_CD IN ('05', '10') / DESC
        5) GOODS_STAT_SCT_CD / ASC
        6) GOODS_NO / DESC
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
            
            # 1) GOODS_STAT_SCT_CD !='03'/ DESC
            stat_sct_cd = metadata.get('GOODS_STAT_SCT_CD', '')
            is_not_03 = 1 if stat_sct_cd != '03' else 0
            
            # 2) APPLIANCES_YN = 'Y' / DESC
            appliances_yn = metadata.get('APPLIANCES_YN', '')
            is_appliance = 1 if appliances_yn == 'Y' else 0
            
            # 3) similarity_rank / ASC (문서 순서 기반 랭크)
            similarity_rank = metadata.get('similarity_rank', 9999)
            
            # 4) GOODS_TP_CD IN ('05', '10') / DESC
            goods_tp_cd = metadata.get('GOODS_TP_CD', '')
            is_target_type = 1 if goods_tp_cd in ('05', '10') else 0
            
            # 5) GOODS_STAT_SCT_CD / ASC
            stat_sct_cd_asc = stat_sct_cd
            
            # 6) GOODS_NO / DESC
            goods_no = metadata.get('GOODS_NO', '')
            
            return (
                -is_not_03,  # DESC
                -is_appliance,  # DESC
                similarity_rank,  # ASC
                -is_target_type,  # DESC
                stat_sct_cd_asc,  # ASC
                -int(goods_no) if goods_no.isdigit() else goods_no  # DESC
            )
        
        return sorted(processed_docs, key=get_sort_key)
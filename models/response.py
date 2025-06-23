"""
Response models for API endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ProductResponse(BaseModel):
    """상품 검색 결과 모델"""
    goodsNo: str = Field(..., description="상품번호")
    goodsStatSctNm: str = Field(..., description="상품상태")
    brndNm: str = Field(..., description="브랜드명")
    goodsNm: str = Field(..., description="상품명")
    artcNm: str = Field(..., description="품목명")
    categoryNm: str = Field(..., description="카테고리명")
    salePrc: int = Field(..., description="판매가")
    # dscntSalePrc: int = Field(..., description="할인가")
    # maxBenefitPrice: int = Field(..., description="최대혜택가")
    cardDcRate: int = Field(..., description="카드할인율")
    cardDcNameList: str = Field(..., description="할인카드")
    featureInfo: str = Field(..., description="주요 특징 및 기능")
    schKwdNm: str = Field(..., description="해시태그")
    saleQty: int = Field(..., description="월간판매량")
    salesUnit: int = Field(..., description="세일즈유닛")
    gdasScrSum: float = Field(..., description="평점")
    gdasCnt: int = Field(..., description="리뷰수")
    energeyGrade: str = Field(..., description="에너지효율등급")
    mdlLnchDt: str = Field(..., description="모델출시일")
    similarity_score: float = Field(..., description="유사도 점수", ge=0.0, le=1.0)
    similarity_rank: int = Field(..., description="유사도 랭킹")
    content: Optional[str] = Field(None, description="상품 내용 미리보기")


class SearchResponse(BaseModel):
    """검색 응답 모델"""
    products: List[ProductResponse] = Field(..., description="검색된 상품 목록")
    total_count: int = Field(..., description="전체 검색 결과 수", ge=0)
    page: int = Field(..., description="현재 페이지", ge=1)
    page_size: int = Field(..., description="페이지 크기", ge=1)
    total_pages: int = Field(..., description="전체 페이지 수", ge=0)
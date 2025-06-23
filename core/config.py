"""
Configuration settings for AI Search API
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # API 설정
    app_name: str = Field("AI Search API", description="애플리케이션 이름")
    app_version: str = Field("1.0.0", description="애플리케이션 버전")
    debug: bool = Field(False, description="디버그 모드")
    
    # 서버 설정
    host: str = Field("localhost", description="서버 호스트")
    port: int = Field(8000, description="서버 포트")
    reload: bool = Field(True, description="자동 재로드")
    
    # OpenAI 설정
    openai_api_key: Optional[str] = Field(None, description="OpenAI API 키")
    embedding_model: str = Field("text-embedding-3-small", description="임베딩 모델")
    
    # 검색 설정
    default_search_k: int = Field(50, description="기본 검색 결과 수")
    max_search_k: int = Field(100, description="최대 검색 결과 수")
    
    # BM25 설정
    bm25_k1: float = Field(1.2, description="BM25 k1 파라미터. 단어빈도 중요도. 높을 수록 단어빈도에 따른 점수 증가. 1.2 ~ 2.0 디폴트 1.2")
    bm25_b: float = Field(0.75, description="BM25 b 파라미터. 문서길이 정규화 정도. 0에 가까울 수록 문서길이의 영향을 덜 받음. 0 ~ 1. 디폴트 0.75")
    
    # FAISS 설정
    faiss_persist_directory: str = Field("./.db/faiss", description="FAISS 데이터베이스 경로")
    
    # 페이지네이션 설정
    default_page_size: int = Field(30, description="기본 페이지 크기")
    max_page_size: int = Field(100, description="최대 페이지 크기")
    
    # 로깅 설정
    log_level: str = Field("INFO", description="로그 레벨")
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 전역 설정 인스턴스
settings = Settings()

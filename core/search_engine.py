import os
import logging
from typing import List
from dotenv import load_dotenv
from core.config import settings
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.schema import Document
from langchain_core.runnables import ConfigurableField

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchEngineManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self):
        if self._initialized:
            return
        
        try:
            # 상수
            persist_directory = settings.faiss_persist_directory
            model = settings.embedding_model
            
            logger.info("검색 엔진 초기화 시작...")
            
            # 환경 변수 로드
            load_dotenv(settings.Config.env_file)
            
            # OpenAI API 키 확인
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
            
            # 임베딩 모델 초기화
            self.embeddings = OpenAIEmbeddings(model=model)

            # FAISS 벡터 스토어 로드
            if os.path.exists(persist_directory):
                self.faiss_db = FAISS.load_local(
                    persist_directory, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"FAISS 데이터베이스 로드 완료: {persist_directory}")
            else:
                logger.error(f"FAISS 데이터베이스를 찾을 수 없습니다: {persist_directory}")
            
            # 검색기 초기화
            # self.faiss_retriever = self.faiss_db.as_retriever(
            #     search_type="similarity", # similarity, similarity_score_threshold, mmr
            #     search_kwargs={
            #         "k": 30, # 상위 30개 결과 반환
            #         # "score_threshold": 0.7, #similarity_score_threshold 일 경우 사용 가능
            #         # "filter": filter_dict
            #     } ,  
            # )
            self.faiss_retriever = self.faiss_db.as_retriever(search_kwargs={"k": 100})

            self.configuable_faiss_retriever = self.faiss_db.as_retriever().configurable_fields(
                search_kwargs=ConfigurableField(
                    # 검색 매개변수의 고유 식별자를 설정
                    id="search_kwargs",
                    # 검색 매개변수의 이름을 설정
                    name="Search Kwargs",
                    # 검색 매개변수에 대한 설명을 작성
                    description="The search kwargs to use",
                )
            )
            
            # BM25 검색기를 위한 문서 준비
            try:
                # FAISS에서 모든 문서 가져오기
                all_docs = self._get_all_documents_from_faiss()
                if all_docs:
                    self.bm25_retriever = BM25Retriever.from_documents(
                        all_docs,
                        # k1=1.2,
                        # b=0.75
                        )
                    self.bm25_retriever.k = 500
                    logger.info(f"BM25 검색기 초기화 완료: {len(all_docs)}개 문서")
                else:
                    logger.warning("BM25 검색기 초기화 실패: 문서가 없습니다")
                    self.bm25_retriever = None
            except Exception as e:
                logger.error(f"BM25 검색기 초기화 실패: {e}")
                self.bm25_retriever = None
            
            # 앙상블 검색기 초기화
            if self.bm25_retriever:
                self.bm25_faiss_73_retriever = EnsembleRetriever(
                    retrievers=[self.bm25_retriever, self.faiss_retriever],
                    weights=[7, 3]  # BM25: 70%, FAISS: 30%
                )
                self.bm25_faiss_37_retriever = EnsembleRetriever(
                    retrievers=[self.bm25_retriever, self.faiss_retriever],
                    weights=[3, 7]  # BM25: 30%, FAISS: 70%
                )
                logger.info("앙상블 검색기 초기화 완료")
            else:
                self.bm25_faiss_73_retriever = self.faiss_retriever
                self.bm25_faiss_37_retriever = self.faiss_retriever
                logger.info("앙상블 검색기 대신 FAISS 검색기만 사용")
            
            self._initialized = True
            logger.info("검색 엔진 초기화 완료!")
            
        except Exception as e:
            logger.error(f"검색 엔진 초기화 실패: {e}")
            raise e
    
    def _get_all_documents_from_faiss(self) -> List[Document]:
        """FAISS에서 모든 문서를 가져오는 헬퍼 메서드"""
        try:
            # FAISS 인덱스에서 문서 정보 추출
            docs = list(self.faiss_db.docstore._dict.values())
            
            return docs
        except Exception as e:
            logger.error(f"FAISS에서 문서 추출 실패: {e}")
            return []
        
    def get_vectorestore(self, retriever_type: str):
        if not self._initialized:
            raise Exception("검색 엔진이 초기화되지 않았습니다.")
        
        if retriever_type == "faiss":
            return self.faiss_db
        else:
            raise ValueError(f"지원하지 않는 검색기 타입: {retriever_type}")
    
    def get_retriever(self, retriever_type: str):
        if not self._initialized:
            raise Exception("검색 엔진이 초기화되지 않았습니다.")
        
        if retriever_type == "bm25":
            if self.bm25_retriever is None:
                logger.warning("BM25 검색기가 없습니다. FAISS 검색기를 대신 사용합니다.")
                return self.faiss_retriever
            return self.bm25_retriever
        elif retriever_type == "faiss":
            return self.faiss_retriever
        elif retriever_type == "bm25_faiss_73":
            return self.bm25_faiss_73_retriever
        elif retriever_type == "bm25_faiss_37":
            return self.bm25_faiss_37_retriever
        elif retriever_type == "configuable_faiss":
            return self.configuable_faiss_retriever
        else:
            raise ValueError(f"지원하지 않는 검색기 타입: {retriever_type}")
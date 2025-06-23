from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Literal
import uvicorn
import logging
from core.search_engine import SearchEngineManager
from services.result_converter import ResultConverter
from services.sort_service import SortService
from models.response import ProductResponse, SearchResponse
from typing import Annotated
from contextlib import asynccontextmanager
from services.pagination_service import PaginationService
from services.intent_service import IntentService
from utils import tokenizer, NL_processor

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# asynccontextmanager 데코레이터를 사용하여 비동기 컨텍스트 매니저를 정의합니다.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 애플리케이션의 라이프사이클 이벤트를 관리합니다.
    서버 시작 시 검색 엔진을 초기화하고, 서버 종료 시 정리 작업을 수행할 수 있습니다.
    """
    try:
        # 서버 시작 시 실행될 코드 (startup)
        search_manager.initialize()
        logger.info("서버 시작 완료")
    except Exception as e:
        logger.error(f"서버 시작 중 오류: {e}")
        logger.warning("오류가 있지만 서버를 계속 시작합니다.")
    
    # 이 yield 문 이전의 코드는 서버 시작 시 실행됩니다.
    # 이 yield 문 이후의 코드는 서버 종료 시 실행됩니다.
    yield
    
    # 서버 종료 시 실행될 코드 (shutdown)
    logger.info("서버 종료 중...")
    # 여기에 필요한 정리 작업 (예: DB 연결 해제, 리소스 반환 등)을 추가할 수 있습니다.
    logger.info("서버 종료 완료")

# FastAPI 애플리케이션에 lifespan 컨텍스트 매니저를 연결합니다.
# 이제 app = FastAPI(lifespan=lifespan)과 같이 인자로 전달합니다.
app = FastAPI(
    lifespan=lifespan,
    title="AI Search API",
    description="AI-powered product search API for e-commerce platform",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 매니저
search_manager = SearchEngineManager()

@app.get("/")
async def root():
    return {
        "message": "AI Search API is running",
        "Swagger_UI_documentation": "http://localhost:8000/docs",
        "ReDoc_documentation": "http://localhost:8000/redoc",
        "description": "서버가 정상적으로 실행 중입니다.",
        "endpoints": {
            "search": "GET /search - 상품 검색"
        }
    }

@app.get("/search", response_model=SearchResponse)
async def search_products(
    query: str = Query(
        default="냉장고",
        description="검색어",
        min_length=1,
        max_length=100
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="페이지 번호"
    ),
    pageSize: int = Query(
        default=30,
        ge=1,
        le=100,
        description="페이지당 결과 수"
    ),
    retriever_type: Annotated[
        Literal["none", "bm25", "faiss", "faiss_with_score", "bm25_faiss_73", "bm25_faiss_37"],
        Query(description="검색 방식")
    ] = "none",
):
    try:
        if not search_manager._initialized:
            raise HTTPException(status_code=503, detail="검색 엔진이 아직 초기화되지 않았습니다.")
        
        if not query.strip():
            raise HTTPException(status_code=400, detail="검색 쿼리가 비어있습니다.")

        
        # # 쿼리가 키워드 기반인지 자연어 인지 판단하여 검색기 선택
        # if retriever_type == "none":
        #     query_type = NL_processor.classify_query_type(query)
        #     logger.info(f"쿼리타입: {query_type}")
        #     if query_type == "keyword":
        #         retriever_type = "bm25_faiss_73"
        #     else:
        #         retriever_type = "bm25_faiss_37"

        # # 검색 수행
        # if retriever_type == "faiss_with_score":
        #     vectorstore = search_manager.get_vectorestore("faiss")
        #     results = vectorstore.similarity_search_with_score(query, k=2)
        #     # for i, (doc, score) in enumerate(results, 1):
        #     #     print(f"유사도: {score}") # 낮을수록 더 유사함
        #     #     print(f"- 상품명: {doc.metadata.get('GOODS_NM', '정보 없음')}")
        #     #     print(f"- 카테고리: {doc.metadata.get('CATEGORY_NMS', '정보 없음')}")
        # elif retriever_type == "bm25" or retriever_type == "bm25_faiss_73":
        #     retriever = search_manager.get_retriever(retriever_type)
        #     # query에서 명사만 추출
        #     tokenized_query = tokenizer.kiwi_tokenized_query(query) 
        #     results = retriever.invoke(tokenized_query)
        # else:
        #     retriever = search_manager.get_retriever(retriever_type)
        #     results = retriever.invoke(query)   

        intent = IntentService.intent_with_llm(query)

        intented_query = intent['NATURAL_LANGUAGE']

        # print(f"NATURAL_LANGUAGE: {intent[NATURAL_LANGUAGE}]")

        retriever = search_manager.get_retriever(retriever_type)
        results = retriever.invoke(intented_query)   

        # 정렬 수행
        sorted_results = SortService.sort_products(results)

        # TODO: 검색어를 key로 캐시를 사용한다면  여기에 구현

        # 정렬된 결과를 페이지네이션 처리
        paginated_results = PaginationService.paginate(
            items=sorted_results,
            page=page,
            page_size=pageSize
        )

        # ResultConverter를 사용하여 결과 변환
        products:ProductResponse = ResultConverter.convert_to_products(paginated_results['items'])
        
        return SearchResponse(
            products=products,
            total_count=paginated_results['total_count'],
            page=paginated_results['current_page'],
            page_size=paginated_results['page_size'],
            total_pages=paginated_results['total_pages']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"에러 발생 라인: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

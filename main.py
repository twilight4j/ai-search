from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Literal
import uvicorn
import logging
import time
from core.search_engine import SearchEngineManager
from core.intent_manager import IntentManager
from core.report_manager import ReportManager
from services.result_service import ResultService
from services.sort_service import SortService
from models.response import ProductResponse, SearchResponse
from typing import Annotated
from contextlib import asynccontextmanager
from services.pagination_service import PaginationService
from services.filter_service import FilterService

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
        intent_manager.initialize()
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
intent_manager = IntentManager()

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
        default="롯데카드 할인되는 20만원대 방수 노이즈캔슬링 이어폰",
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
        default=10,
        ge=1,
        le=100,
        description="페이지당 결과 수"
    ),
    retriever_type: Annotated[
        Literal["bm25", "faiss", "bm25_faiss_73", "bm25_faiss_37", "intent_with_llm"],
        Query(description="검색 방식")
    ] = "intent_with_llm",
):
    """
    # 추천검색어
    분류|키워드
    --|--
    제품특징, 가격 필터링 | 방수되는 20만원대 노이즈캔슬링 이어폰
    제품특징, 가격 필터링, 할인카드 | 롯데카드 할인되는 20만원대 방수 노이즈캔슬링 이어폰
    제품특징, 브랜드 | 100만원대 삼성 OLED 스마트TV 가성비 좋은 모델
    제품특징, 평점 필터링 | 평점이 4.5 이상인 4도어 냉장고 추천해주세요
    """
    try:
        timestamp = time.time()
        if not search_manager._initialized:
            raise HTTPException(status_code=503, detail="검색 엔진이 아직 초기화되지 않았습니다.")
        
        if not intent_manager._initialized:
            raise HTTPException(status_code=503, detail="의도분석 LLM이 아직 초기화되지 않았습니다.")
        
        if not query.strip():
            raise HTTPException(status_code=400, detail="검색 쿼리가 비어있습니다.")

        #  검색할 최대 문서 수
        top_k = 100
        # 의도
        intent = {}

        # [검색]
        if retriever_type == "intent_with_llm":

            # 1. 의도 분석
            # LLM을 통한 의도 분석
            intent_chain = intent_manager.get_intent_chain()
            intent = intent_chain.invoke({"query": query})
            print(f"🤔 의도 분석: {intent}")

            # 정제된 쿼리
            intented_query = intent['INTENTED_QUERY']
            print(f"🔍 정제된 쿼리: {intented_query}")

            # 2. 필터 생성
            # 의도 기반 필터
            filter_dict = FilterService.intent_based_filtering(query, intent)
            print(f"✂️ 필터: {filter_dict}")

            # 3. 검색
            # 의도 기반 사용자 쿼리와 필터를 넣고 검색
            retriever = search_manager.get_retriever("configuable_faiss")

            config = {"configurable": {"search_kwargs": {
                "k": top_k, # 최종적으로 반환할 문서 수
                "fetch_k": 500, # FAISS로부터 가져올 초기 문서 수
                "filter": filter_dict
            }}}

            results = retriever.invoke(intented_query, config=config)

        else:
            retriever = search_manager.get_retriever(retriever_type)
            results = retriever.invoke(query)

        # [정렬]
        sorted_results = SortService.sort_products(results, top_k, intent)

        # TODO: 검색어를 key로 캐시를 사용한다면 여기에 구현

        # [페이징]
        paginated_results = PaginationService.paginate(
            items=sorted_results,
            page=page,
            page_size=pageSize
        )

        # [결과 변환]
        products:List[ProductResponse] = ResultService.convert_to_products(paginated_results['items'])
        
        print(f"⌛ 총 소요 시간: {time.time() - timestamp:.2f}초")
        
        return SearchResponse(
            intent=str(intent),
            intented_query=intented_query,
            filter_dict=str(filter_dict),
            total_count=paginated_results['total_count'],
            page=paginated_results['current_page'],
            page_size=paginated_results['page_size'],
            total_pages=paginated_results['total_pages'],
            products=products
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

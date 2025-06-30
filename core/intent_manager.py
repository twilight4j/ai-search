import logging
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentManager:
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

            logger.info("의도분석 LLM 초기화 시작...")

            # 원하는 데이터 구조를 정의합니다.
            class Intent(BaseModel):
                INTENTED_QUERY: str = Field(description="사용자 검색어에서 가격 관련 내용은 제거하고 자연스런 문장으로 변환.")
                PRICE_GTE: int = Field(description="가격범위 최소값. 예를 들어 100만원 이상 120만원 이하이면, 1000000. 가격에 대한 의도가 없다면 0.")
                PRICE_LTE: int = Field(description="가격범위 최대값. 예를 들어 100만원 이상 120만원 이하이면, 1200000. 가격에 대한 의도가 없다면 0.")
                BRND_NM: str = Field(description="브랜드명")
                ARTC_NM: str = Field(description="찾고 있는 상품의 품목. 예를 들어 에어컨, 냉장고, TV, 이어폰, 보조배터리 등.")
                LGRP_NM: list[str] = Field(description="""카테고리명. 다음 예시 중 적합한 카테고리 최대 3개. 
            TV·영상가전
            가구·인테리어
            태블릿·이북리더기
            건강가전
            게임기·타이틀
            냉장고·주방가전
            레저·여행·헬스케어
            렌탈·구독
            휴대폰·스마트워치
            생활·주방용품
            세탁기·건조기·의류관리기
            에어컨·계절가전(description=공기청정기, 냉난방기 포함)
            청소기·생활가전
            카메라
            컴퓨터·노트북
            스마트홈
            음향가전
            뷰티·이미용가전
            문구·악기·공구
            안심케어(description=가전제품 클리닝, 교체, 이사, 재설치 등의 서비스)
            방문컨설팅(description=가전제품 고장, 수리 서비스)
            전문가 화상상담(description=영상통화로 구매 상담이 가능한 제품 모음)
            1인 가구를 위한 나노스퀘어(description=1인 세대를 위한 소형가전 모음)""")
                FEATURES: str = Field(description="주요기능")
                CARD_DC_NMS: list[str] = Field(description="할인카드이름")
                REVIEW_GTE: float = Field(description="리뷰점수 최소값. 예를들어 3.0 이상 5.0 이하이면 3.0. 평점에 대한 의도가 없다면 0.0.")
                REVIEW_LTE: float = Field(description="리뷰점수 최대값. 예를들어 3.0 이상 5.0 이하이면 5.0. 평점에 대한 의도가 없다면 0.0.")

            # 파서를 설정하고 프롬프트 템플릿에 지시사항을 주입합니다.
            parser = JsonOutputParser(pydantic_object=Intent)
            # print(parser.get_format_instructions())

            # 프롬프트를 생성합니다.
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "당신은 가전전문 e커머스 검색 AI 어시스턴트 입니다. 사용자의 검색어를 분석하여, 그 의도에 맞는 최적의 검색 필터 조건을 완성해야 합니다."),
                    ("user", "#Format: {format_instructions}\n\n#Question: {query}"),
                ]
            )

            prompt = prompt.partial(format_instructions=parser.get_format_instructions())

            # # OpenAI 객체를 생성합니다.
            model = ChatOpenAI(temperature=0, model_name="gpt-4.1-mini")

            # 체인을 구성합니다.
            self.intent_chain = prompt | model | parser

            self._initialized = True
            logger.info(f"의도분석 LLM 체인구성 완료!")
            
        except Exception as e:
            logger.error(f"의도분석 LLM 초기화 실패: {e}")
            raise e
    
    def get_intent_chain(self):
        """
        의도분석 LLM 체인을 반환합니다.
        [LLM 사용법]
            intent_chain = intent_manager.get_intent_chain()
            intent = intent_chain.invoke({"query": query})
        """
        if not self._initialized:
            raise Exception("의도분석 LLM 이 아직 초기화되지 않았습니다.")
        return self.intent_chain
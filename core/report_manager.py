import logging
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportManager:
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

            logger.info("리포트 LLM 초기화 시작...")

            # 원하는 데이터 구조를 정의합니다.
            class Report(BaseModel):
                goodsNo: str = Field(..., description="상품번호")
                recommendation: str = Field(..., description="상품 추천 이유")

            # 파서를 설정하고 프롬프트 템플릿에 지시사항을 주입합니다.
            parser = JsonOutputParser(pydantic_object=Report)
            # print(parser.get_format_instructions())

            # 프롬프트를 생성합니다.
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "당신은 가전전문 e커머스 상품 추천 AI 어시스턴트 입니다. 사용자 검색어(Question)를 참고하여 상품 추천 이유를 간단하고. 친절하게 설명해주세요. 주어진 Context 외 확인되지 않은 사실을 이야기 해서는 안됩니다. 응답속도는 최대한 빨리 부탁해요."),
                    ("user", "#Format: {format_instructions}\n\n#Context: {context}\n\n#Question: {query}"),
                ]
            )

            prompt = prompt.partial(format_instructions=parser.get_format_instructions())

            # OpenAI 객체를 생성합니다.
            model = ChatOpenAI(temperature=0, model_name="gpt-4.1-mini")

            # 체인을 구성합니다.
            self.report_chain = prompt | model | parser

            self._initialized = True
            logger.info(f"리포트 LLM 체인구성 완료!")
            
        except Exception as e:
            logger.error(f"리포트 LLM 초기화 실패: {e}")
            raise e
    
    def get_report_chain(self):
        """
        리포트 LLM 체인을 반환합니다.
        [LLM 사용법]
            report_chain = report_manager.get_report_chain()
            report = report_chain.invoke({"query": query, "context": context})
        """
        if not self._initialized:
            raise Exception("리포트 LLM 이 아직 초기화되지 않았습니다.")
        return self.report_chain

    # LLM 을 통한 검색 백업 코드(미사용)
    @staticmethod
    def search_proudct(query, retriever):
        """
        LLM 사용자 쿼리의 의도를 분석합니다.
        """

        # 원하는 데이터 구조를 정의합니다.
        class ProductResponse(BaseModel):
            """상품 검색 결과 모델"""
            goodsNo: str = Field(..., description="상품번호")
            recommendation: str = Field(..., description="상품 추천 이유")

        # 파서를 설정하고 프롬프트 템플릿에 지시사항을 주입합니다.
        parser = JsonOutputParser(pydantic_object=ProductResponse)
        # print(parser.get_format_instructions())

        # 프롬프트를 생성합니다.
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "당신은 가전전문 e커머스 검색 AI 어시스턴트 입니다. 적합한 품목의 상품으로 상품을 100개 이상 추천해주세요."),
                ("user", "#Format: {format_instructions}\n\n#Context: {context}\n\n#Question: {question}"),
            ]
        )

        prompt = prompt.partial(format_instructions=parser.get_format_instructions())

        # # OpenAI 객체를 생성합니다.
        model = ChatOpenAI(temperature=0, model_name="gpt-4.1-mini")

        # 체인을 구성합니다.
        chain = (
            {"context": retriever.invoke, "question": RunnablePassthrough()}
            | prompt 
            | model 
            | parser
            )

        # 체인을 호출하여 쿼리 실행
        answer = chain.invoke(query)

        return answer
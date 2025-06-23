from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class IntentService:
    @staticmethod

    def intent_with_llm(query):
        """
        LLM 사용자 쿼리의 의도를 분석합니다.
        """

        # 원하는 데이터 구조를 정의합니다.
        class Filter(BaseModel):
            NATURAL_LANGUAGE: str = Field(description="사용자 검색어를 자연스러운 요구형 문장으로 변환.")
            SALE_PRC_GTE: int = Field(description="가격범위 최소값. 예를 들어 100만원 이상 120만원 이하이면, 1000000")
            SALE_PRC_LTE: int = Field(description="가격범위 최대값. 예를 들어 100만원 이상 120만원 이하이면, 1200000")
            BRND_NM: str = Field(description="브랜드명")
            ARTC_NM: str = Field(description="품목")
            LGRP_NM: str = Field(description="""카테고리명. 다음 카테고리 예시 중 반드시 1개. 
        안심케어
        전문가 화상상담
        1인 가구를 위한 나노스퀘어 
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
        에어컨·계절가전
        청소기·생활가전
        카메라
        컴퓨터·노트북
        스마트홈
        음향가전
        뷰티·이미용가전
        문구·악기·공구
        가전 수리비 보장 가전보험
        방문컨설팅""")
            FEATURES: str = Field(description="주요기능")

        # 파서를 설정하고 프롬프트 템플릿에 지시사항을 주입합니다.
        parser = JsonOutputParser(pydantic_object=Filter)
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
        chain = prompt | model | parser

        # 체인을 호출하여 쿼리 실행
        answer = chain.invoke({"query": query})

        return answer
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class LLMService:
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
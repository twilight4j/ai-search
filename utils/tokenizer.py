from kiwipiepy import Kiwi

_kiwi = None

def kiwi_tokenized_query(text):
    global _kiwi
    if _kiwi is None:
        _kiwi = Kiwi()

    tokens = _kiwi.tokenize(text)

    # 1. 'tag'가 'NNG'인 토큰의 'form' (원형)만 추출하여 리스트 생성
    nng_forms = [token.form for token in tokens if token.tag == 'NNG']

    # 2. 추출된 명사들을 공백(' ')으로 연결하여 하나의 문자열로 반환
    result_string = " ".join(nng_forms)
    
    print(f"형태소분석을 거쳐 변환된 쿼리: {result_string}")

    return result_string
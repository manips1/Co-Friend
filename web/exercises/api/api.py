import openai
import json
import requests


def create_problem(keywords):
    """
    문제, 예시 코드 생성 함수

    :param keywords: keyword list
    :return: problem and example code dict
    """
    problem_sentence = create_problem_sentence(keywords)
    exam_code = generate_code(problem_sentence)

    return {'problem': problem_sentence,
            'code': exam_code}


def create_problem_sentence(keywords):
    """
    문제 문장 생성 함수

    키워드 -> openai model -> 문제

    :param keywords: keyword list
    :return: problem sentence string
    """

    """
    문제 생성 요청문 생성
    """
    request_str = 'Create a python problem sentence about '
    for keyword in keywords:
        request_str += '{} and '.format(keyword)
    request_str = request_str[:-5]
    request_str += '.'

    """
    API request & response

    model: 모델 이름
    prompt: 요청 내용
    temperature: 값이 낮을수록 안정적인 값 출력
    stop: 문장 출력 종료 조건
    """
    response = openai.Completion.create(
        model='davinci:ft-cofriend-2022-10-20-10-23-31',
        prompt=request_str,
        temperature=0.7,
        stop=['.']
        )
    # json 파싱
    json_object = json.loads(response.__str__())
    result_text = json_object['choices'][0]['text']

    # 결과 반환
    return result_text + '.'


def generate_code(problem_sentence):
    """
    문제에 맞는 예시 코드 생성 함수

    문제 -> openai model -> 예시 코드

    :param problem_sentence: problem string
    :return: python code string
    """

    """
    API request & response

    engine: 사용할 엔진, GPT-3의 자식이라고 할 수 있는 Codex 엔진 사용
    temperature: 값이 낮을수록 안정적인 값 출력
    instruction: 요청 내용
    """
    response = openai.Edit.create(
        engine="code-davinci-edit-001",
        temperature=0,
        instruction=problem_sentence
    )

    # json 파싱
    json_object = json.loads(response.__str__())
    result_text = json_object['choices'][0]['text']

    return result_text


def compile_code(code, input='', language='python'):
    """
    입력된 String code data 컴파일

    :param code: code string
    :param language: language string
    :return: result
    """
    if language == 'python':
        lang = 'py'
    else:
        return 'Unknown language'

    url = 'https://codex-api.herokuapp.com/'

    data = {
      'code': code,
      'language': lang,
      'input': input
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
      }

    r = requests.post(url=url, headers=headers, data=data)
    try:
        j = r.json()
    except:
        return 'Compile server error'
    
    if j['success']:
        return j['output']
    else:
        return j['error']

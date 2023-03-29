import openai
import json

"""
요청 내용
"""
request_str = 'Create a python problem sentence about print and if.'

request_str2 = """
Code A is:
first_name = input("Enter your first name: ")
last_name = input("Enter your last name: ")

print(last_name + " " + first_name)

Code B is:
fname = input("Input your First Name : ")
lname = input("Input your Last Name : ")
print ("Hello  " + lname + " " + fname)

Code B is a answer code.

Grade Code A.

Please answer this format:
['grade': True or False,
'reason':text]
"""

"""
API request & response

model: 모델 이름
prompt: 요청 내용
temperature: 값이 낮을수록 안정적인 값 출력
stop: 문장 출력 종료 조건
"""
response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[
        {"role": "user", "content": request_str2}
    ]
    )
# json 파싱
json_object = json.loads(response.__str__())
result_text = json_object['choices'][0]['message']['content']

#결과 출력
print(result_text + '.')
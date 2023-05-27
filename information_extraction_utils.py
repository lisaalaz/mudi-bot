import openai
from retry import retry

from secret_key import key 

openai.api_key = key # You will need your own OpenAI API key.

@retry()
def contains_number(text):
  for i in reversed(range(1,27)):
    if str(i) in text:
      return str(i)
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Write the number, in digits, contained in the following text. Write the number and nothing else (no punctuation). \
              If the text does not contain a number, just say 'no number': {text}"}
        ]
      )
  answer = api_response['choices'][0]['message']['content']
  return answer.lower()

# @retry()
# def wants_to_end(text):
#   api_response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system",
#              "content": f"does the speaker of the following utterance imply that they wish to end the conversation and leave? (reply just yes or no): {text}"}
#         ]
#      )
#   answer = api_response['choices'][0]['message']['content']
#   if "yes" in answer.lower():
#     answer = True
#   else:
#     answer = False
#   return answer
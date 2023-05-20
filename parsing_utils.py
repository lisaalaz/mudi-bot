import copy
import openai
import re
import torch
from retry import retry
from transformers import AutoModelForMaskedLM
from tokenizers import ByteLevelBPETokenizer
from tokenizers.processors import BertProcessing

from prompting_utils import username
from sat_utils import add_exercises
from secret_key import key 

openai.api_key = key # You will need your own OpenAI API key.

device = "cuda" if torch.cuda.is_available() else "cpu"

labels = ['not_s', 's']
label2int = dict(zip(labels, list(range(len(labels)))))

class ClassificationModel(torch.nn.Module):
    def __init__(self, base_model, n_classes, base_model_output_size=768, dropout=0.05):
        super().__init__()
        self.base_model = base_model
        
        self.classifier = torch.nn.Sequential(
            torch.nn.Dropout(dropout),
            torch.nn.Linear(base_model_output_size, base_model_output_size),
            torch.nn.Mish(),
            torch.nn.Dropout(dropout),
            torch.nn.Linear(base_model_output_size, n_classes)
        )
        
        for layer in self.classifier:
            if isinstance(layer, torch.nn.Linear):
                layer.weight.data.normal_(mean=0.0, std=0.02)
                if layer.bias is not None:
                    layer.bias.data.zero_()

    def forward(self, input_):
        X, attention_mask = input_
        hidden_states = self.base_model(X, attention_mask=attention_mask)
        
        return self.classifier(hidden_states[0][:, 0, :])
    
with torch.no_grad():
  s_model = ClassificationModel(AutoModelForMaskedLM.from_pretrained("roberta-base").base_model, len(labels))
  s_model.load_state_dict(torch.load('models/RoBERTa_s_intention.pt', map_location=torch.device(device)))

def is_s_intention(text):
  text = re.sub(r'[^\w\s]', '', text)
  text = text.lower()

  t = ByteLevelBPETokenizer(
            "models/tokenizer/vocab.json",
            "models/tokenizer/merges.txt"
        )
  t._tokenizer.post_processor = BertProcessing(
            ("</s>", t.token_to_id("</s>")),
            ("<s>", t.token_to_id("<s>")),
        )
  t.enable_truncation(512)
  t.enable_padding(pad_id=t.token_to_id("<pad>"))
  tokenizer = t

  encoded = tokenizer.encode(text)
  sequence_padded = torch.tensor(encoded.ids).unsqueeze(0)
  attention_mask_padded = torch.tensor(encoded.attention_mask).unsqueeze(0)
   
  output = s_model((sequence_padded, attention_mask_padded))
  _, top_class = output.topk(1, dim=1)
  label = int(top_class[0][0])
  label_map = {v: k for k, v in label2int.items()}
  label = label_map[label]
  return True if label=="s" else False

@retry()
def is_answer(question, reply):
  # Whether user's reply answers bot's utterance or not.
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": f"Given utterance_A: {question} and utterance_B: {reply}, does utterance_B answer utterance_A? Answer yes or no."}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "yes" in answer.lower():
    answer = True
  else:
    answer = False
  return answer

@retry()
def is_question(text):
  # Establishes whether the user's utterance contains a question for the bot to answer.
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Does the following sentence contain a question (answer only yes or no): {text}"}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "yes" in answer.lower():
    answer = True
  else:
    answer = False
  return answer

@retry()
def is_answer_positive(question, reply):
  if "yes" in reply.lower():
    return True
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": f"Person_A: {question} Person_B: {reply}. Did Person_B answer 'yes' or 'no' to Person_A's question? Just say yes or no."}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "yes" in answer.lower():
    answer = True
  else:
    answer = False
  return answer

@retry()
def is_specific(question, reply):
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": f"Person_A: {question} Person_B: {reply}. Did Person_B answer that something specific caused the feeling or that it's just a general feeling? Just say specific or general."}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "specific" in answer.lower():
    answer = True
  else:
    answer = False
  return answer

@retry()
def event_classification(text):
  # Whether user's utterance describes an event, and whether it is personal or not.
  is_event = False
  personal_or_impersonal = ""
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": f"[Input]: My cat died last week. [Is it an event and is it personal]: yes, personal. [Input]: I want to kill myself. [Is it an event and is it personal]: no, not an event. \
             [Input]: I had a terrible fight with my sister and I am sad now. [Is it an event and is it personal]: yes, personal. [Input]: Joe Biden has won the election. [Is it an event and is it personal]: yes, not personal. \
             [Input]: I went to cemetery the other day, to visit my father's grave. He died a long time ago. [Is it an event and is it personal]: yes, personal. \
             [Input]: I hope I can find a boyfriend. [Is it an event and is it personal]: no, not an event. [Input]: The Mets are playing a match tomorrow. [Is it an event and is it personal]: yes, not personal. \
             [Input]: I am quite sad. [Is it an event and is it personal]: no, not an event. [Input]: Everyone is becoming stupid in this country. [Is it an event and is it personal]: yes, not personal. \
             [Input]: I just want to die. [Is it an event and is it personal]: no, not an event. [Input]: {text}. [Is it an event and is it personal]:"}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "yes" in answer.lower():
    is_event = True
  if "impersonal" in answer.lower():
    personal_or_impersonal = "impersonal"
  elif "personal" in answer.lower():
    personal_or_impersonal = "personal"
  return is_event, personal_or_impersonal

@retry()
def extract_event(text):
  # Extracts very short summary of described event.
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": f"Input: My cat died last week. Summary: {username}'s cat died. Input: I had a terrible fight with my sister and I am sad now. Summary: {username} had a fight with their sister. Input: I went to cemetery the other day, to visit my father's grave. He died a long time ago. Summary: {username} went to the cemetery. Input: {text}. Summary:"}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  return answer

@retry()
def past_or_future_event(text):
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Is the main event described in the following text in the past or the future: {text}. Answer only the word 'past' or 'future'."}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "future" in answer.lower():
    answer = "future"
  else:
    answer = "past"
  return is_answer

@retry()
def recent_or_distant_event(text):
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Classify the event described in the following text as recent or distant: {text}. Distant events are those that happened 10 years ago or more. Just answer recent or distant. \
              If there is no indication of time, answer unknown."}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "distant" in answer.lower():
    answer = "distant"
  else:
    answer = "recent"
  return answer

@retry()
def is_emotion(text):
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"[Input]: My cat died last week. [Does it express an emotion]: no. [Input]: I had a terrible fight with my sister and I am sad now. [Does it express an emotion]: yes. \
              [Input]: Yes thank you. [Does it express an emotion]: no. [Input]: Joe Biden has won the election. [Does it express an emotion]: no. \
              [Input]: I went to cemetery the other day, to visit my father's grave. He died a long time ago. [Does it express an emotion]: no. [Input]: I love my boyfriend. [Does it express an emotion]: yes. \
              [Input]: The Mets are playing a match tomorrow. [Does it express an emotion]: no. [Input]: I am quite anxious. [Does it express an emotion]: yes. \
              [Input]: Everyone is becoming stupid in this country. [Does it express an emotion]: no. [Input]: Ok. [Does it express an emotion]: no. [Input]: {text}. [Does it express an emotion]:"}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "yes" in answer.lower():
    answer = True
  else:
    answer = False
  return answer

@retry()
def emotion_classification(text):
  emotions_list = ["happiness", "contentment", "sadness", "fear", "anxiety", "anger", "love", "insecurity", "disgust", "disappointment", "shame", "guilt", "envy", "jealousy"]
  emotion = "neutral"
  degree = ""
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Out of the following emotions: {', '.join(emotions_list)}, which of these emotions is expressed in the following text, and how intense is it, out of low, medium or high? \
              Just state the intensity and the emotion name, for example 'high sadness': {text}"}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  for emo in emotions_list:
      if emo in answer.lower():
        emotion = emo
  for d in ["low", "medium", "high"]:
      if d in answer.lower():
        degree = d
  return emotion, degree

@retry()
def is_emotion_negative(emotion):
  answer = True
  if emotion.lower() in ["happiness", "contentment", "love", "neutral"]:
    answer = False
  return answer

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

@retry()
def wants_to_end(text):
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": f"does the speaker of the following utterance imply that they wish to end the conversation and leave? (reply just yes or no): {text}"}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "yes" in answer.lower():
    answer = True
  else:
    answer = False
  return answer

def drop_existing_keys(dict1, dict2):
  new_dict = copy.deepcopy(dict1)
  for key in dict1:
    if key in dict2:
      del new_dict[key]
  return new_dict

def parse_user_message(global_emotions_map, global_events_map, prompt, sat_exercises, curr_exercise_number):
  emotions_map = {}
  events_map = {}
  s_intention = is_s_intention(prompt)
  curr_exercise_number = contains_number(prompt)
  is_event, _ = event_classification(prompt)
  emotion_detected = is_emotion(prompt)
  if emotion_detected:
    emotion, degree = emotion_classification(prompt)
    is_negative = is_emotion_negative(emotion)
    sat_exercises = add_exercises(emotion, is_negative, sat_exercises)
  else:
    emotion, degree = ("", "")

  if is_event:
    event_summary = extract_event(prompt)
    events_map[event_summary] = {}
    event_time = recent_or_distant_event(prompt)
    events_map[event_summary]["time_of_event"] = event_time
    if emotion_detected and emotion != "neutral":
        events_map[event_summary]["resulting_emotion"] = emotion
        emotions_map[emotion] = {}
        emotions_map[emotion]["intensity"] = degree
        emotions_map[emotion]['cause'] = event_summary
    else:
        events_map[event_summary]["resulting_emotion"] = None
  elif emotion_detected and emotion != "neutral":
      emotions_map[emotion] = {}
      emotions_map[emotion]["intensity"] = degree
      emotions_map[emotion]['cause'] = None

  emotions_map = drop_existing_keys(emotions_map, global_emotions_map)
  events_map = drop_existing_keys(events_map, global_events_map)

  global_emotions_map.update(emotions_map)
  global_events_map.update(events_map)
  return global_emotions_map, global_events_map, emotions_map, events_map, sat_exercises, curr_exercise_number, s_intention
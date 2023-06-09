import openai
import torch
from retry import retry
from transformers import LlamaTokenizer, LlamaForCausalLM, pipeline, set_seed, logging

from prompting_utils import prompts, user_names, assistant_names, task_prediction_prompt
from secret_key import key

openai.api_key = key # You will need your own OpenAI API key.
logging.FATAL

def load_model(model_type):
    if model_type=="koala-13B":
        tokenizer = LlamaTokenizer.from_pretrained(f"models/koala_13B_vanilla")
        model = LlamaForCausalLM.from_pretrained(f"models/koala_13B_vanilla", load_in_8bit=True,
                                                 torch_dtype=torch.float16, device_map='auto')
    elif model_type=="vicuna-13B":
        tokenizer = LlamaTokenizer.from_pretrained(f"models/vicuna-13b-1.1")
        model = LlamaForCausalLM.from_pretrained(f"models/vicuna-13b-1.1", load_in_8bit=True,
                                                 torch_dtype=torch.float16, device_map='auto')
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=512,
                         temperature=0.7, top_p=0.95, repetition_penalty=1.15)
    return pipe

@retry()
def create_response(messages, model_type, pipe, task_prompt=""):
    if model_type == "gpt-3.5-turbo":
        api_response = openai.ChatCompletion.create(
            model=model_type,
            messages=messages,
        )
        bot_utterance = api_response['choices'][0]['message']['content']
    else:
        prompt = prompts[model_type].format(extract_turns(messages, model_type), task_prompt)
        #print(prompt)
        set_seed(42)
        response = pipe(prompt, do_sample=True, return_full_text=False)
        bot_utterance = response[0]['generated_text']
        if f"{user_names[model_type]}:" in bot_utterance:
            bot_utterance = bot_utterance.split(f"{user_names[model_type]}:")[0]
    return bot_utterance.strip()

def extract_turns(messages, model_type):
    previous_context = [turn for turn in messages if turn["role"] == "assistant" or turn["role"] == "user"]
    if len(previous_context) > 10:
        previous_context = previous_context[-10:]
    context_string = []
    for turn in previous_context:
        if turn["role"] == "user":
            context_string.append(f"{user_names[model_type]}: {turn['content']}")
        elif turn["role"] == "assistant":
            context_string.append(f"{assistant_names[model_type]}: {turn['content']}")
    extracted_turns = " ".join(context_string)
    return extracted_turns

@retry()
def label_tasks(context):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=task_prediction_prompt.format(context),
        temperature=0.5,
        max_tokens=64,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1,
    )
    return response['choices'][0]['text']


import openai
import torch

import transformers
from transformers import AutoTokenizer, LlamaTokenizer, LlamaForCausalLM, OPTForCausalLM, TextGenerationPipeline, pipeline, set_seed

from prompting_utils import gpt_instruction_prompt, opt_koala_initial_prompt, opt_koala_instruction_prompt, username
from secret_key import key # You will need your own OpenAI API key to insert below
openai.api_key = key

#device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model(model_type):
    if model_type == 'opt':
        tokenizer = AutoTokenizer.from_pretrained("models/opt-2.7b")
        model = OPTForCausalLM.from_pretrained("models/opt-2.7b", device_map='auto')
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=512, temperature=0.7, top_p=0.95, repetition_penalty=1.15)
    elif model_type == 'koala':
        tokenizer = LlamaTokenizer.from_pretrained("models/koala-7b")
        model = LlamaForCausalLM.from_pretrained("models/koala-7b", device_map='auto')
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=512, temperature=0.7, top_p=0.95, repetition_penalty=1.15)
    elif model_type == 'gpt-3.5-turbo':
        model = None
        tokenizer = None
    return model, tokenizer, pipe


def create_response(messages, model_type, pipe, task_prompt=""):
    if model_type == "gpt-3.5-turbo":
        api_response = openai.ChatCompletion.create(
            model=model_type,
            messages=messages,
        )
        bot_utterance = api_response['choices'][0]['message']['content']
    elif model_type == "opt" or model_type == "koala":
        prompt = " ".join([opt_koala_initial_prompt, opt_koala_instruction_prompt.format(
                  extract_turns(messages), task_prompt)])
        print(prompt)
        set_seed(42)
        response = pipe(prompt, do_sample=True, return_full_text=False)
        bot_utterance = response[0]['generated_text']
        if model_type == "opt":
            bot_utterance = bot_utterance.split("MiTa: ")[1].split(f"{username}:")[0]
    return bot_utterance
    

def extract_turns(messages):
    previous_context = [turn for turn in messages if turn["role"] == "assistant" or turn["role"] == "user"]
    if len(previous_context) > 6:
        previous_context = previous_context[-6:]
    context_string = []
    for turn in previous_context:
        if turn["role"] == "user":
            context_string.append(f"{username}: {turn['content']}")
        elif turn["role"] == "assistant":
            context_string.append(f"MiTa: {turn['content']}")
    extracted_turns = "\n".join(context_string)
    return extracted_turns
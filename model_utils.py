import openai
import torch

import transformers
from transformers import AutoTokenizer, LlamaTokenizer, LlamaForCausalLM, OPTForCausalLM, TextGenerationPipeline, pipeline, set_seed

from prompting_utils import gpt_prompt, instruction_prompt, opt_prompt, koala_prompt, username
from secret_key import key # You will need your own OpenAI API key to insert below
openai.api_key = key

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model(model_type):
    if model_type == 'opt':
        tokenizer = AutoTokenizer.from_pretrained("models/opt-2.7b")
        model = OPTForCausalLM.from_pretrained("models/opt-2.7b").to(device)
        pipe = TextGenerationPipeline(model=model, tokenizer=tokenizer, device=device)
    elif model_type == 'koala':
        tokenizer = LlamaTokenizer.from_pretrained("models/koala-7b")
        model = LlamaForCausalLM.from_pretrained("models/koala-7b", device_map='auto')
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_length=512, temperature=0.7, top_p=0.95, repetition_penalty=1.15)
    elif model_type == 'gpt-3.5-turbo':
        model = None
        tokenizer = None
        pipe = None
    return model, tokenizer, pipe

def create_response(messages, model_type, model, tokenizer, pipe, task_prompt=None):
    if model_type == "gpt-3.5-turbo":
        api_response = openai.ChatCompletion.create(
            model=model_type,
            messages=messages,
        )
        bot_utterance = api_response['choices'][0]['message']['content']
    elif model_type == "opt":
        if task_prompt is None:
            prompt = [opt_prompt, extract_turns(messages, model_type), "MiTa: "]
        else:
            prompt = [opt_prompt, extract_turns(messages, model_type), "MiTa: ", instruction_prompt, task_prompt]
        prompt = "\n".join(prompt)
        #print(prompt)
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
        response = model.generate(input_ids, max_new_tokens=1024)
        bot_utterance = tokenizer.decode(response[0], skip_special_tokens=True)
        set_seed(42)
        #response = pipe(prompt, max_length=256, early_stopping=True, do_sample=True, num_beams=3,
                            #repetition_penalty=3.0, num_return_sequences=1, return_full_text=False)
        #response = pipe(prompt, max_length=256, do_sample=True)
        #bot_utterance = response[0]['generated_text']
    elif model_type == "koala":
        if task_prompt is None:
            prompt = koala_prompt.format(
                f"Answer the following sentence with empathy as if you're a psychotherapist: {extract_turns(messages, model_type)}")
        else:
            prompt = koala_prompt.format(task_prompt)
        print(prompt)
        response = pipe(prompt)
        bot_utterance = response[0]['generated_text']
    return bot_utterance
    

def extract_turns(messages, model_type):
    previous_context = [turn for turn in messages if turn["role"] == "assistant" or turn["role"] == "user"]
    if len(previous_context) > 10:
        previous_context = previous_context[-10:]
    context_string = []
    if model_type == "opt":
        for turn in previous_context:
            if turn["role"] == "user":
                context_string.append(f"{username}: {turn['content']}")
            elif turn["role"] == "assistant":
                context_string.append(f"MiTa: {turn['content']}")
        extracted_turns = "\n".join(context_string)
    elif model_type == "koala":
        extracted_turns = previous_context[-1]["content"]
    return extracted_turns
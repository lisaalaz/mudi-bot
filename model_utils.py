import openai
import torch

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, OPTForCausalLM, TextGenerationPipeline, set_seed

from prompting_utils import gpt_prompt, instruction_prompt, opt_prompt, dial_flant5_prompt, username
from secret_key import key # You will need your own OpenAI API key to insert below
openai.api_key = key

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model(model_type):
    if model_type == 'opt':
        tokenizer = AutoTokenizer.from_pretrained("models/opt-2.7b")
        model = OPTForCausalLM.from_pretrained("models/opt-2.7b").to(device)
        pipeline = TextGenerationPipeline(model=model, tokenizer=tokenizer, device=device)
    elif model_type == 'DIAL-FLANT5-XL':
        tokenizer = AutoTokenizer.from_pretrained("models/koala-7B-HF")
        model = AutoModelForSeq2SeqLM.from_pretrained("models/koala-7B-HF", device_map="auto")
        pipeline = None
    elif model_type == 'gpt-3.5-turbo':
        model = None
        tokenizer = None
        pipeline = None
    return model, tokenizer, pipeline

def create_response(messages, model_type, model, tokenizer, pipeline, task_prompt=None):
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
        #response = pipeline(prompt, max_length=256, early_stopping=True, do_sample=True, num_beams=3,
                            #repetition_penalty=3.0, num_return_sequences=1, return_full_text=False)
        #response = pipeline(prompt, max_length=256, do_sample=True)
        #bot_utterance = response[0]['generated_text']
    elif model_type == "DIAL-FLANT5-XL":
        if task_prompt is None:
            prompt = dial_flant5_prompt.format("Answer nicely", extract_turns(messages, model_type), "Answers nicely")
        else:
            prompt = dial_flant5_prompt.format(task_prompt, extract_turns(messages, model_type), task_prompt)
        print(prompt)
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
        response = model.generate(input_ids, max_new_tokens=1024)
        bot_utterance = tokenizer.decode(response[0], skip_special_tokens=True)
    return bot_utterance
    

def extract_turns(messages, model_type):
    previous_context = messages[-1]
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
    elif model_type == "DIAL-FLANT5-XL":
        for turn in previous_context:
            context_string.append(turn)
        extracted_turns = " [ENDOFTURN] ".join(context_string)
    return extracted_turns
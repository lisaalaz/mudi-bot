import openai
import torch

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, OPTForCausalLM, TextGenerationPipeline, set_seed

from secret_key import key # You will need your own OpenAI API key to insert below
openai.api_key = key

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model(model_type):
    if model_type == 'opt':
        tokenizer = AutoTokenizer.from_pretrained("models/opt-2.7b")
        model = OPTForCausalLM.from_pretrained("models/opt-2.7b").to(device)
        #pipeline = TextGenerationPipeline(model=model, tokenizer=tokenizer, device=device)
    elif model_type == 'DIAL-FLANT5-XL':
        tokenizer = AutoTokenizer.from_pretrained("models/DIAL-FLANT5-XL")
        model = AutoModelForSeq2SeqLM.from_pretrained("models/DIAL-FLANT5-XL", device_map="auto")
    elif model_type == 'gpt-3.5-turbo':
        model = None
        tokenizer = None
    return model, tokenizer

def create_response(messages, model_type, model, tokenizer, task_prompt=None):
    if model_type == "gpt-3.5-turbo":
        api_response = openai.ChatCompletion.create(
            model=model_type,
            messages=messages,
        )
        bot_utterance = api_response['choices'][0]['message']['content']
    elif model_type == "opt":
        prompt = [messages[0]["content"], task_prompt, extract_turns(messages, model_type)]
        prompt = "\n".join(prompt)
        prompt += f"\nMiTa:"
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
        set_seed(42)
        response = model.generate(input_ids, do_sample=True)
        bot_utterance = tokenizer.batch_decode(response, skip_special_tokens=True)
    elif model_type == "DIAL-FLANT5-XL":
        prompt = [f"Instruction: {task_prompt}", f"Input: {extract_turns(messages, model_type)}", f"[QUESTION] An empathetic response that also {task_prompt} is:"]
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
        response = model.generate(input_ids)
        bot_utterance = tokenizer.decode(response[0], skip_special_tokens=True)
    return bot_utterance
    

def extract_turns(messages, model_type): # TODO: write function to collect relevant dialogue formats for each model
    if model_type == "opt":
        pass
    elif model_type == "DIAL-FLANT5-XL":
        pass
    return ""
import colorama
import openai
import queue

import microtask_utils
import parsing_utils

from prompting_utils import username, instruction_prompt, system_prompt

from secret_key import key # You will need your own OpenAI API key to insert below
openai.api_key = key


def chatbot():
  prompt = instruction_prompt
  messages = [
      {"role": "system", 
       "content": system_prompt},
       {"role": "user", 
       "content": "Hello MiTa"},
  ]
  global_emotions_map = {}
  # structure:
  # {emotion1: {
  #    "intensity": str,
  #    "cause": str,   
  #    },
  #  emotion2: {
  #    "intensity": str,
  #    "cause": str,   
  #    },
  # }
  global_events_map = {}
  # structure:
  # {event1: {
  #    "time_of_event": str,
  #    "resulting_emotion": str,
  #    },
  #  event2: {
  #    "time_of_event": str,
  #    "resulting_emotion": str,
  #    },
  # }
  available_tasks = microtask_utils.load_microtasks()
  active_tasks = queue.PriorityQueue(maxsize=10)
  removed_tasks = []
  sat_exercises = []
  end_conversation = False
  current_wait_turns = 0

  while not end_conversation:
    active_tasks, _ = microtask_utils.listify_queue(active_tasks, True)

    if current_wait_turns > 0:
      print(f"waiting {current_wait_turns} turn/s before starting any next task")
      current_wait_turns -= 1
    api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
      )
    bot_utterance = api_response['choices'][0]['message']['content']
    messages.append({"role": "assistant", "content": bot_utterance})
    print(colorama.Style.RESET_ALL)
    print(colorama.Back.BLUE + colorama.Fore.WHITE + f"MiTa: {bot_utterance}")
    print(colorama.Back.GREEN + colorama.Fore.WHITE)
    user_utterance = input(f"{username}: ")
    print(colorama.Style.RESET_ALL)
    end_conversation = parsing_utils.wants_to_end(user_utterance)
    global_emotions_map, global_events_map, emotions_map, events_map, sat_exercises = parsing_utils.parse_user_message(global_emotions_map, global_events_map, user_utterance, sat_exercises)
    messages.append({"role": "user", "content": user_utterance})
    
    active_tasks = microtask_utils.add_microtasks(emotions_map, events_map, available_tasks, active_tasks, removed_tasks)
  
    while active_tasks.qsize() > 0 and current_wait_turns <= 0:
        #if microtasks[i].get_arg("is_active"): # sanity check if mt is active
        current_mt = active_tasks.get(block=False)[1]
        current_wait_turns = current_mt.get_wait_turns_on_exit()
        active_tasks, active_tasks_list = microtask_utils.listify_queue(active_tasks, False)
        print(f"Current active microtasks: {[x.get_identifier() for x in active_tasks_list]}") #[x.get_identifier() for x in microtasks if x.get_arg('is_active')]
        print(f"Completed and aborted microtasks: {[x.get_identifier() for x in removed_tasks]}")
        print(f"Executing microtask: {current_mt.get_identifier()}")
        messages, exercises, active_tasks, end_conversation, removed_tasks = current_mt.execute_task(messages, sat_exercises, prompt, 
                                                                                                     available_tasks, active_tasks, removed_tasks, 
                                                                                                     global_emotions_map, global_events_map)
        
  if end_conversation:
    messages.append({"role": "system", 
       "content": f"{username} Needs to go now. Say goodbye to {username} and end the conversation until next time."})
    api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
      )
    bot_utterance = api_response['choices'][0]['message']['content']
    messages.append({"role": "assistant", "content": bot_utterance})
    print(colorama.Style.RESET_ALL)
    print(colorama.Back.BLUE + colorama.Fore.WHITE + f"MiTa: {bot_utterance}")
    print(colorama.Style.RESET_ALL)
    print("--------CONVERSATION ENDED--------")


if __name__ == "__main__":
    chatbot()
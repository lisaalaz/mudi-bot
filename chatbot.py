import colorama
import queue

import microtask_utils
from model_utils import load_model, create_response
import parsing_utils
from prompting_utils import gpt_initial_prompt, prompts, username

def chatbot(model_type):
  if model_type != "gpt-3.5-turbo":
     model, tokenizer, pipeline = load_model(model_type)
  else:
     pipeline = None
  prompt = prompts[model_type]
  messages = [
      {"role": "system",
       "content": gpt_initial_prompt},
       {"role": "user",
       "content": "Hello"},
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
  current_task = microtask_utils.Microtask("none")
  available_tasks = microtask_utils.load_microtasks()
  active_tasks = queue.PriorityQueue(maxsize=10)
  removed_tasks = []
  sat_exercises = []
  s_intention = False
  country = None
  current_ex_number = "no number"
  end_conversation = False
  current_wait_turns = 0

  while not end_conversation:
    active_tasks, _ = microtask_utils.listify_queue(active_tasks, True)

    if current_wait_turns > 0:
      print(f"waiting {current_wait_turns} turn/s before starting any next task")
      current_wait_turns -= 1
    bot_utterance = create_response(messages, model_type, pipeline)
    messages.append({"role": "assistant", "content": bot_utterance})
    print(colorama.Style.RESET_ALL)
    print(colorama.Back.WHITE + colorama.Fore.BLACK + f"MiTa: {bot_utterance}")
    print(colorama.Back.WHITE + colorama.Fore.BLACK)
    user_utterance = input(f"{username}: ")
    print(colorama.Style.RESET_ALL)
    end_conversation = parsing_utils.wants_to_end(user_utterance)
    global_emotions_map, global_events_map, emotions_map, events_map, sat_exercises, current_ex_number, s_intention = parsing_utils.parse_user_message(global_emotions_map, global_events_map,
                                                                                                                                             user_utterance, sat_exercises, current_ex_number)
    messages.append({"role": "user", "content": user_utterance})

    active_tasks, s_intention = microtask_utils.add_microtasks(emotions_map, events_map, s_intention, available_tasks, active_tasks, removed_tasks, current_task)

    while active_tasks.qsize() > 0 and current_wait_turns <= 0:
        current_task = active_tasks.get(block=False)[1]
        current_wait_turns = current_task.get_wait_turns_on_exit()(removed_tasks)
        active_tasks, active_tasks_list = microtask_utils.listify_queue(active_tasks, False)
        print(f"Current active microtasks: {[x.get_identifier() for x in active_tasks_list]}")
        print(f"Completed and aborted microtasks: {[x.get_identifier() for x in removed_tasks]}")
        print(f"Executing microtask: {current_task.get_identifier()}")
        messages, sat_exercises, current_ex_number, s_intention, country, active_tasks, end_conversation, removed_tasks = current_task.execute_task(messages, sat_exercises, current_ex_number, prompt,
                                                                                                     available_tasks, active_tasks, removed_tasks, current_task,
                                                                                                     global_emotions_map, global_events_map, model_type, pipeline, country)
  if end_conversation:
    messages.append({"role": "system",
       "content": f"{username} Needs to go now. Say goodbye to {username} and end the conversation until next time."})
    bot_utterance = create_response(messages, model_type, pipeline)
    messages.append({"role": "assistant", "content": bot_utterance})
    print(colorama.Style.RESET_ALL)
    print(colorama.Back.WHITE + colorama.Fore.BLACK + f"MiTa: {bot_utterance}")
    print(colorama.Style.RESET_ALL)
    print("--------CONVERSATION ENDED--------")

if __name__ == "__main__":
    chatbot("gpt-3.5-turbo")
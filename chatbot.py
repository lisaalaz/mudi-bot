import colorama
import queue

import task_utils
from model_utils import load_model, create_response
from prompting_utils import gpt_initial_prompt, username, botname
import sat_utils

def chatbot(model_type):
  if model_type != "gpt-3.5-turbo":
    pipeline = load_model(model_type)
  else:
     pipeline = None
  messages = [
      {"role": "system",
       "content": gpt_initial_prompt},
       {"role": "user",
       "content": "Hello"},
  ]
  current_task = task_utils.Microtask("none")
  available_tasks = task_utils.load_microtasks()
  active_tasks = queue.PriorityQueue(maxsize=10)
  finished_tasks = []
  sat_exercises = []
  current_ex_number = "no number"
  #end_conversation = False
  current_wait_turns = 0

  while True:
    active_tasks, active_tasks_list = task_utils.listify_queue(active_tasks, True)
    sat_exercises = sat_utils.add_exercises(active_tasks_list, current_task, sat_exercises)

    if current_wait_turns > 0:
      print(f"waiting {current_wait_turns} turn/s before starting any next goal")
      current_wait_turns -= 1
    bot_utterance = create_response(messages, model_type, pipeline)
    messages.append({"role": "assistant", "content": bot_utterance})
    print(colorama.Style.RESET_ALL)
    print(colorama.Back.WHITE + colorama.Fore.BLACK + f"{botname}: {bot_utterance}")
    print(colorama.Back.WHITE + colorama.Fore.BLACK)
    user_utterance = input(f"{username}: ")
    print(colorama.Style.RESET_ALL)
    #end_conversation = information_extraction_utils.wants_to_end(user_utterance)
    messages.append({"role": "user", "content": user_utterance})

    active_tasks = task_utils.add_tasks(messages, available_tasks, active_tasks, finished_tasks, current_task)

    while active_tasks.qsize() > 0 and current_wait_turns <= 0:
        current_task = active_tasks.get(block=False)[1]
        current_wait_turns = current_task.get_wait_turns_on_exit()(finished_tasks)
        active_tasks, active_tasks_list = task_utils.listify_queue(active_tasks)
        if current_task.is_resumed():
           print(f"Resuming goal: {current_task.get_name()}")
        else:
           print(f"Executing goal: {current_task.get_name()}")
        messages, sat_exercises, current_ex_number, active_tasks, finished_tasks = current_task.execute_task(messages, sat_exercises, current_ex_number, available_tasks,
                                                                                                            active_tasks, finished_tasks, current_task, model_type, pipeline)
#   if end_conversation:
#     messages.append({"role": "system",
#        "content": f"{username} Needs to go now. Say goodbye to {username} and end the conversation until next time."})
#     bot_utterance = create_response(messages, model_type, pipeline)
#     messages.append({"role": "assistant", "content": bot_utterance})
#     print(colorama.Style.RESET_ALL)
#     print(colorama.Back.WHITE + colorama.Fore.BLACK + f"{botname}: {bot_utterance}")
#     print(colorama.Style.RESET_ALL)
#     print("--------CONVERSATION ENDED--------")

if __name__ == "__main__":
    chatbot("gpt-3.5-turbo")
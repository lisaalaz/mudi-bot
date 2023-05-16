import colorama
import copy
import math

import parsing_utils
import sat_utils

from model_utils import create_response
from mt_attributes import mt_attributes
from prompting_utils import username


class Microtask():
  def __init__(self, task_name):
    #immutable attributes
    self.name = task_name
    self.task_type = mt_attributes[task_name]["type"]
    self.priority = mt_attributes[task_name]["priority"]
    self.enter_condition = mt_attributes[task_name]["enter_condition"]
    self.expires_after = mt_attributes[task_name]["expires_after"]
    self.wait_turns_on_exit = mt_attributes[task_name]["wait_turns_on_exit"]
    self.dag = mt_attributes[task_name]["dag"]
    
    #mutable attributes
    self.reference = None
    self.pointer = 0
    self.turns_since_added = 0

  def __eq__(self, compare_with):
    return self.priority == compare_with.priority
  
  def __lt__(self, compare_with):
    return self.priority < compare_with.priority
  
  def __gt__(self, compare_with):
    return self.priority > compare_with.priority

  def get_name(self):
    return self.name

  def get_type(self):
    return self.task_type

  def add_reference(self, reference):
    self.reference = reference

  def get_reference(self):
    return self.reference

  def get_identifier(self):
    return self.name.format(self.reference)

  def get_priority(self):
    return self.priority

  def get_enter_condition(self):
    return self.enter_condition

  def get_n_turns(self):
    return self.n_turns

  def exit(self):
    self.is_active = False

  def get_wait_turns_on_exit(self):
    return self.wait_turns_on_exit

  def get_status(self):
    return self.is_active

  def get_pointer(self):
    return self.pointer

  def get_turns_since_added(self):
    return self.turns_since_added

  def move_pointer_forward(self):
    self.pointer += 1

  def increase_turn_counter(self):
    self.turns_since_added += 1

  def remove_task(self, active_tasks, removed_tasks):
    removed_tasks.append(self)
    return active_tasks, removed_tasks

  def execute_task(self, messages, exercises, chosen_ex_number, prompt, available_tasks, active_tasks, removed_tasks, current_task, global_emotions_map, global_events_map, model_type, model, tokenizer, pipeline):
    end_conversation = False
    continue_task = True

    reference_to_pass = ""
    if self.turns_since_added > 0:
      reference_to_pass = self.reference

    current_turn = list(self.dag.keys())[0]

    while continue_task and not end_conversation: #and self.pointer < len(self.dag):
        bot_turn, user_turn, messages, exercises, chosen_ex_number, active_tasks, end_conversation = turn(self.dag[current_turn]["question"][model_type], reference_to_pass, messages, exercises, chosen_ex_number,
                                                                                        prompt, available_tasks, active_tasks, removed_tasks, current_task, global_emotions_map, global_events_map,
                                                                                        model_type, model, tokenizer, pipeline)
        choice = self.dag[current_turn]["continue_condition"](bot_turn, user_turn)
        #print(f"The choice is {choice}")
        if end_conversation:
            print(f"Aborted microtask: {self.get_identifier()}")
        elif choice == "abort":
            active_tasks, removed_tasks = self.remove_task(active_tasks, removed_tasks)
            print(f"Aborted microtask: {self.get_identifier()}")
            continue_task = False
        elif choice == "end":
            active_tasks, removed_tasks = self.remove_task(active_tasks, removed_tasks)
            print(f"Completed microtask: {self.get_identifier()}")
            continue_task = False
        else:
            current_turn = choice
 
        self.move_pointer_forward()
        self.increase_turn_counter()

    return messages, exercises, chosen_ex_number, active_tasks, end_conversation, removed_tasks


def add_to_queue(microtask, reference, q):
    task_to_add = copy.deepcopy(microtask)
    task_to_add.add_reference(reference)
    q.put((task_to_add.get_priority(), task_to_add), False)
    return q


def listify_queue(q, increase_turn_counter_switch):
  q_copy = []
  while not q.empty():
    elem = q.get(False)
    q_copy.append(elem[1])
  for x in q_copy:
    if increase_turn_counter_switch:
      x.increase_turn_counter()
    q.put((x.get_priority(), x), False)
  return q, q_copy


def add_microtasks(emotions_map, events_map, available_tasks, active_tasks, removed_tasks, current_task):
  for mt in available_tasks:
    if mt.get_type() == "emotion":
      for emotion in emotions_map:
        event = ""
        active_tasks, active_tasks_list = listify_queue(active_tasks, False)
        enter_condition = mt.get_enter_condition()(emotion, event, removed_tasks, active_tasks_list, current_task)
        if enter_condition: 
          active_tasks = add_to_queue(mt, emotion, active_tasks)
          print(f"Added microtask: {mt.get_name().format(emotion)}")
    elif mt.get_type() == "event":
      for event in events_map:
        emotion = ""
        active_tasks, active_tasks_list = listify_queue(active_tasks, False)
        enter_condition = mt.get_enter_condition()(emotion, event, removed_tasks, active_tasks_list, current_task)
        if enter_condition:
          active_tasks = add_to_queue(mt, event, active_tasks)
          print(f"Added microtask: {mt.get_name().format(event)}")
  return active_tasks


def load_microtasks():
  available_microtasks = []
  for key in mt_attributes:
    available_microtasks.append(Microtask(key))
  return available_microtasks


def turn(question, task_reference, messages, sat_exercises, chosen_ex_number, prompt, available_tasks, all_tasks, removed_tasks, current_task, global_emotions_map, global_events_map, model_type, model, tokenizer, pipeline):
  if question:
    messages.append({"role": "system", "content": f"{prompt}" + question.format(task_reference)})
  if question == "ask the following question in a respectful way (you may paraphrase it slightly) without adding any further sentences: I can recommend the following exercises, please let me know which one you would like.":
    message = [{"role": "system", "content": question.format(task_reference)}]
    bot_turn = create_response(message, model_type, model, tokenizer, pipeline, task_prompt=question.format(task_reference))
    print(colorama.Style.RESET_ALL)
    print(colorama.Back.WHITE + colorama.Fore.BLACK + f"MiTa: {bot_turn}")    
    sat_utils.show_recommendations(sat_exercises)
  elif question == "ask the following question in a respectful way (you may paraphrase it slightly) without adding any further sentences: Please go to the exercise now, and let me know once you have done it. If for any reason you cannot do it right now, just let me know.":
    message = [{"role": "system", "content": question.format(task_reference)}]
    bot_turn = create_response(message, model_type, model, tokenizer, pipeline, task_prompt=question.format(task_reference))
    sat_exercises.remove(sat_utils.exercise_titles[int(chosen_ex_number)])
    print(colorama.Style.RESET_ALL)
    print(colorama.Back.WHITE + colorama.Fore.BLACK + f"MiTa: {sat_utils.show_exercise_instructions(chosen_ex_number)}\n{bot_turn}")    
  else:
    bot_turn = create_response(messages, model_type, model, tokenizer, pipeline, task_prompt=f"{prompt}" + question.format(task_reference))
    print(colorama.Style.RESET_ALL)
    print(colorama.Back.WHITE + colorama.Fore.BLACK + f"MiTa: {bot_turn}")    
  
  print(colorama.Back.WHITE + colorama.Fore.BLACK)
  user_turn = input(f'{username}: ')
  print(colorama.Style.RESET_ALL)
  global_emotions_map, global_events_map, emotions_map, events_map, sat_exercises, chosen_ex_number = parsing_utils.parse_user_message(global_emotions_map, global_events_map, user_turn, sat_exercises, chosen_ex_number)
  end = parsing_utils.wants_to_end(user_turn)
  
  all_tasks = add_microtasks(emotions_map, events_map, available_tasks, all_tasks, removed_tasks, current_task)
  if question:
    del messages[-1]

  messages.append({"role": "assistant", "content": bot_turn})
  messages.append({"role": "user", "content": user_turn})

  return bot_turn, user_turn, messages, sat_exercises, chosen_ex_number, all_tasks, end





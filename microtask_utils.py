import colorama
import copy
import math

import helpline_utils
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
    self.resumed = False

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
  
  def set_resumed(self, value):
    self.resumed = value
  
  def is_resumed(self):
    return self.resumed

  def get_turns_since_added(self):
    return self.turns_since_added

  def move_pointer_forward(self):
    self.pointer += 1

  def increase_turn_counter(self):
    self.turns_since_added += 1

  def remove_task(self, active_tasks, removed_tasks):
    removed_tasks.append(self)
    return active_tasks, removed_tasks
  
  def hold_task(self, active_tasks):
    self.resumed = True
    active_tasks.put((self.get_priority(), self), False)
    return active_tasks

  def execute_task(self, messages, exercises, chosen_ex_number, prompt, available_tasks, active_tasks, removed_tasks, current_task, global_emotions_map, global_events_map, model_type, pipeline, country):
    end_conversation = False
    continue_task = True

    reference_to_pass = ""
    #if self.turns_since_added > 0:
    reference_to_pass = self.reference

    while continue_task and not end_conversation:
        current_pointer = self.get_pointer()
        current_turn = list(self.dag.keys())[current_pointer]
        previous_turn = list(self.dag.keys())[current_pointer-1]
        question = " ".join(
        [f"and provide a very short summary of what you said earlier to go back to the previous topic (hint: what you said was {self.dag[previous_turn]['question'].split(' (HINT:')[0]}) and",
        self.dag[current_turn]["question"]]) if self.is_resumed() else " ".join(["and", self.dag[current_turn]["question"]])
        self.set_resumed(False)
        bot_turn, user_turn, messages, exercises, chosen_ex_number, s_intention, country, active_tasks, end_conversation = turn(
                                                                                        question, reference_to_pass, messages, exercises, chosen_ex_number,
                                                                                        prompt, available_tasks, active_tasks, removed_tasks, current_task,
                                                                                        global_emotions_map, global_events_map, model_type, pipeline, country)
        _, active_tasks_list = listify_queue(active_tasks, False)
        choice = self.dag[current_turn]["continue_condition"](bot_turn, user_turn, active_tasks_list, current_task)
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
        elif choice == "wait":
            active_tasks = self.hold_task(active_tasks)
            print(f"Held microtask: {self.get_identifier()}")
            continue_task = False
        else:
            current_turn = choice
 
        self.move_pointer_forward()
        self.increase_turn_counter()

    return messages, exercises, chosen_ex_number, s_intention, country, active_tasks, end_conversation, removed_tasks


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


def add_microtasks(emotions_map, events_map, s_intention, available_tasks, active_tasks, removed_tasks, current_task):
  print(f"s_intention is {s_intention}")
  for mt in available_tasks:
    if mt.get_type() == "emotion":
      #print(f"for selecting {mt.get_name()} s_intention is {s_intention}")
      for emotion in emotions_map:
        event = ""
        active_tasks, active_tasks_list = listify_queue(active_tasks, False)
        enter_condition = mt.get_enter_condition()(s_intention, emotion, event, removed_tasks, active_tasks_list, current_task)
        if enter_condition: 
          active_tasks = add_to_queue(mt, emotion, active_tasks)
          print(f"Added microtask: {mt.get_name().format(emotion)}")
    elif mt.get_type() == "event":
      #print(f"for selecting {mt.get_name()} s_intention is {s_intention}")
      for event in events_map:
        emotion = ""
        active_tasks, active_tasks_list = listify_queue(active_tasks, False)
        enter_condition = mt.get_enter_condition()(s_intention, emotion, event, removed_tasks, active_tasks_list, current_task)
        if enter_condition:
          active_tasks = add_to_queue(mt, event, active_tasks)
          print(f"Added microtask: {mt.get_name().format(event)}")
    elif mt.get_type() == "intention":
      #print(f"for selecting {mt.get_name()} s_intention is {s_intention}")
      intention = ""
      active_tasks, active_tasks_list = listify_queue(active_tasks, False)
      enter_condition = mt.get_enter_condition()(s_intention, None, None, removed_tasks, active_tasks_list, current_task)
      if enter_condition:
          active_tasks = add_to_queue(mt, intention, active_tasks)
          print(f"Added microtask: {mt.get_name().format(intention)}")
  s_intention = False
  return active_tasks, s_intention


def load_microtasks():
  available_microtasks = []
  for key in mt_attributes:
    available_microtasks.append(Microtask(key))
  return available_microtasks


def turn(question, task_reference, messages, sat_exercises, chosen_ex_number, prompt, available_tasks, all_tasks,
         removed_tasks, current_task, global_emotions_map, global_events_map, model_type, pipeline, country):
  if question:
    messages.append({"role": "system", "content": f"{prompt}" + question.format(task_reference)})
  if "recommend the following exercises" in question:
    messages.append({"role": "system", "content": f"{prompt}" + question.format(task_reference)})
    bot_turn = create_response(messages, model_type, pipeline, task_prompt=question.format(task_reference))
    if "\n" in bot_turn:
      bot_turn = bot_turn.split("\n")[0].strip()
    print(colorama.Style.RESET_ALL)
    print(colorama.Back.WHITE + colorama.Fore.BLACK + f"MiTa: {bot_turn}")    
    sat_utils.show_recommendations(sat_exercises)
  elif "go through the exercise" in question:
    messages.append({"role": "system", "content": f"{prompt}" + question.format(task_reference)})
    bot_turn = create_response(messages, model_type, pipeline, task_prompt=question.format(task_reference))
    if "\n" in bot_turn:
      bot_turn = bot_turn.split("\n")[0].strip()
    sat_exercises.remove(sat_utils.exercise_titles[int(chosen_ex_number)])
    print(colorama.Style.RESET_ALL)
    print(colorama.Back.WHITE + colorama.Fore.BLACK + f"MiTa: {sat_utils.show_exercise_instructions(chosen_ex_number)}\n{bot_turn}")
  elif "list of helplines" in question:
    messages.append({"role": "system", "content": f"{prompt}" + question.format(task_reference)})
    bot_turn = create_response(messages, model_type, pipeline, task_prompt=question.format(task_reference))
    if "\n" in bot_turn:
      bot_turn = bot_turn.split("\n")[0].strip()
    print(colorama.Style.RESET_ALL)
    print(colorama.Back.WHITE + colorama.Fore.BLACK + f"MiTa: {bot_turn}\n{helpline_utils.show_helplines(country)}")
  else:
    if model_type == "gpt-3.5-turbo":
        bot_turn = create_response(messages, model_type, pipeline, task_prompt=f"{prompt}" + question.format(task_reference))
    else:
        bot_turn = create_response(messages, model_type, pipeline, task_prompt=question.format(task_reference))
    print(colorama.Style.RESET_ALL)
    print(colorama.Back.WHITE + colorama.Fore.BLACK + f"MiTa: {bot_turn}")
  
  print(colorama.Back.WHITE + colorama.Fore.BLACK)
  user_turn = input(f'{username}: ')
  print(colorama.Style.RESET_ALL)
  if "what country you are located in" in question:
    country = helpline_utils.get_country(user_turn)
  global_emotions_map, global_events_map, emotions_map, events_map, sat_exercises, chosen_ex_number, s_intention = parsing_utils.parse_user_message(global_emotions_map, global_events_map, user_turn, sat_exercises, chosen_ex_number)
  end = parsing_utils.wants_to_end(user_turn)
  
  all_tasks, s_intention = add_microtasks(emotions_map, events_map, s_intention, available_tasks, all_tasks, removed_tasks, current_task)
  if question:
    del messages[-1]

  messages.append({"role": "assistant", "content": bot_turn})
  messages.append({"role": "user", "content": user_turn})
  print(f"{prompt}" + question.format(task_reference))
  return bot_turn, user_turn, messages, sat_exercises, chosen_ex_number, s_intention, country, all_tasks, end





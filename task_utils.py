import colorama
import copy

import information_extraction_utils
import sat_utils

from model_utils import create_response, label_tasks
from task_attributes import task_attributes
from prompting_utils import username, botname, user_names


class Microtask():
  def __init__(self, task_name):
    #immutable attributes
    self.name = task_name
    self.priority = task_attributes[task_name]["priority"]
    self.expires_after = task_attributes[task_name]["expires_after"]
    self.wait_turns_on_exit = task_attributes[task_name]["wait_turns_on_exit"]
    self.dag = task_attributes[task_name]["dag"]
    
    #mutable attributes
    self.pointer = 0
    self.turns_since_added = 0
    self.reference = None
    self.resumed = False
    self.last_utterance = None

  def __eq__(self, compare_with):
    return self.priority == compare_with.priority
  
  def __lt__(self, compare_with):
    return self.priority < compare_with.priority
  
  def __gt__(self, compare_with):
    return self.priority > compare_with.priority

  def get_name(self):
    return self.name

  def get_priority(self):
    return self.priority
  
  def get_expires_after(self):
    return self.expires_after

  def exit(self):
    self.is_active = False

  def get_wait_turns_on_exit(self):
    return self.wait_turns_on_exit

  def set_reference(self, utterance):
    self.reference = utterance

  def get_reference(self):
    return self.reference

  def get_pointer(self):
    return self.pointer
  
  def get_dag(self):
    return self.dag
  
  def set_resumed(self, value):
    self.resumed = value
  
  def is_resumed(self):
    return self.resumed
  
  def set_last_utterance(self, utterance):
    self.last_utterance = utterance

  def get_last_utterance(self):
    return self.last_utterance

  def get_turns_since_added(self):
    return self.turns_since_added

  def move_pointer_forward(self):
    self.pointer += 1

  def increase_turn_counter(self):
    self.turns_since_added += 1

  def remove_task(self, finished_tasks):
    finished_tasks.append(self)
    return finished_tasks
  
  def hold_task(self, active_tasks):
    self.resumed = True
    active_tasks.put((self.get_priority(), self), False)
    return active_tasks

  def execute_task(self, messages, exercises, chosen_ex_number, available_tasks, active_tasks, finished_tasks, current_task, model_type, pipeline):
    #end_conversation = False
    continue_task = True

    while continue_task:
        current_pointer = self.get_pointer()
        current_turn = list(self.dag.keys())[current_pointer]
        instruction = " ".join(
        [f"mention again what was said earlier (hint: what was said was {self.get_last_utterance()}) and then,",
        self.get_dag()[current_turn]["instruction"]]) if self.is_resumed() else (
          " ".join([self.get_dag()[current_turn]["instruction"],
                    f"(hint: this is related to what {username} said before, that is: {self.get_reference()})",]
                    ) if self.get_turns_since_added() > 5 else self.get_dag()[current_turn]["instruction"])
        self.set_resumed(False)
        messages, exercises, chosen_ex_number, active_tasks = turn(instruction, messages, exercises, chosen_ex_number, available_tasks,
                                                                   active_tasks, finished_tasks, current_task, model_type, pipeline)
        _, active_tasks_list = listify_queue(active_tasks)
        
        if any(x.get_priority() < current_task.get_priority() for x in active_tasks_list):
          print(f"Suspending '{current_task.get_name()}' goal")
          current_task.set_last_utterance(messages[-3]["content"])
          active_tasks = current_task.hold_task(active_tasks)
          continue_task = False

        else:
          self.move_pointer_forward()
          if self.get_pointer() == len(list(self.dag.keys())):
            self.remove_task(finished_tasks)
            continue_task = False

    return messages, exercises, chosen_ex_number, active_tasks, finished_tasks


def add_to_queue(task, q):
    task_to_add = copy.deepcopy(task)
    q.put((task_to_add.get_priority(), task_to_add), False)
    return q


def listify_queue(q, increase_turn_counter_switch=False):
  q_copy = []
  while not q.empty():
    elem = q.get(False)
    q_copy.append(elem[1])
  for x in q_copy:
    if increase_turn_counter_switch:
      x.increase_turn_counter()
    if x.get_turns_since_added() < x.get_expires_after():
      q.put((x.get_priority(), x), False)
  return q, q_copy


def add_tasks(messages, available_tasks, active_tasks, finished_tasks, current_task):
  added = False
  _, active_tasks_list = listify_queue(active_tasks)
  context = [turn for turn in messages if turn["role"] == "assistant" or turn["role"] == "user"]
  context = context[-2:]
  context_list = []
  for turn in context:
      if turn["role"] == "assistant":
            context_list.append(f"Assistant: {turn['content']}")
      elif turn["role"] == "user":
          context_list.append(f"User: {turn['content']}")
  context_string = " ".join(context_list)

  labels_string = label_tasks(context_string)
  for task in available_tasks:
    if task.get_name() in labels_string and task not in (active_tasks_list + finished_tasks) and current_task.get_name() != task.get_name():
      task.set_reference(context_string.split("User: ")[1])
      active_tasks = add_to_queue(task, active_tasks)
      print(f"Added goal: {task.get_name()}")
      added = True
  if added:
    _, active_tasks_list = listify_queue(active_tasks)
    print(f"Queued goals: {[x.get_name() for x in active_tasks_list]}")
    print(f"Completed goals: {[x.get_name() for x in finished_tasks]}")
  return active_tasks


def load_microtasks():
  available_microtasks = []
  for key in task_attributes:
    available_microtasks.append(Microtask(key))
  return available_microtasks


def turn(instruction, messages, sat_exercises, chosen_ex_number, available_tasks, all_tasks, finished_tasks, current_task, model_type, pipeline):
  exercise_string = ", ".join(sat_exercises)
  try:
    exercise_instructions = "\n".join(sat_utils.exercise_texts[int(chosen_ex_number)])
  except:
    exercise_instructions = None
  if instruction:
    messages.append({"role": "system", "content": instruction.format(user=user_names[model_type], exercise_list=exercise_string,
                                                                     exercise_instructions=exercise_instructions)})
  bot_turn = create_response(messages, model_type, pipeline, task_prompt=instruction.format(user=user_names[model_type],
                                                                                            exercise_list=exercise_string,
                                                                                            exercise_instructions=exercise_instructions))
  print(colorama.Style.RESET_ALL)
  print(colorama.Back.WHITE + colorama.Fore.BLACK + f"{botname}: {bot_turn}")
  
  print(colorama.Back.WHITE + colorama.Fore.BLACK)
  user_turn = input(f'{username}: ')
  print(colorama.Style.RESET_ALL)
  if "which exercise they would like" in instruction:
    chosen_ex_number = information_extraction_utils.contains_number(user_turn)
    try:
      sat_exercises.remove(sat_utils.exercise_titles[int(chosen_ex_number)])
    except:
      pass
  #end = information_extraction_utils.wants_to_end(user_turn)
  if instruction:
    del messages[-1]

  messages.append({"role": "assistant", "content": bot_turn})
  messages.append({"role": "user", "content": user_turn})
  all_tasks = add_tasks(messages, available_tasks, all_tasks, finished_tasks, current_task)

  return messages, sat_exercises, chosen_ex_number, all_tasks





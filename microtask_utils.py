import colorama
import copy
import math
import openai

import parsing_utils
import sat_utils

from prompting_utils import username

from secret_key import key # You will need your own OpenAI API key to insert below
openai.api_key = key


mt_attributes = {
  "investigate event causing {} emotion": {
      "type": "emotion",
      "priority": 1, 
      "wait_turns_on_exit": 2,
      "enter_condition": lambda emotion, event, removed_tasks, active_tasks_list: (parsing_utils.is_emotion_negative(emotion) and not any(x.get_name()=="investigate event causing {} emotion" for x in active_tasks_list + removed_tasks)), 
      "expires_after": math.inf, 
      "dag": {
          "ask_event": {
              "question": "ask what caused this {} feeling, or whether it is just a general feeling. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any further questions apart from this.",
              "continue_condition": lambda bot_turn, user_turn: "ask_what_happened" if (parsing_utils.is_answer(bot_turn, user_turn) and parsing_utils.is_specific(bot_turn, user_turn)) else "abort",
          },
          "ask_what_happened": {
              "question": "ask if they can say a little more about what happened that caused the {} feelings. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions apart from this.",
              "continue_condition": lambda bot_turn, user_turn: "end" if parsing_utils.is_answer(bot_turn, user_turn) else "abort",
           },
         }, 
      },
  "investigate event '{}'": {
      "type": "event",
      "priority": 2, 
      "wait_turns_on_exit": 1,
      "enter_condition": lambda emotion, event, removed_tasks, active_tasks_list: (not any(x.get_name() == "investigate event '{}'" for x in active_tasks_list + removed_tasks)),
      "expires_after": math.inf, 
      "dag": {
          "ask_when_event_happened": {
              "question": "ask when the event {} happened. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions apart from this.",
              "continue_condition": lambda bot_turn, user_turn: "end" if (parsing_utils.is_answer(bot_turn, user_turn)) else "abort",
           },
         }, 
      },
  "investigate emotion caused by event '{}'": {
      "type": "event",
      "priority": 3, 
      "wait_turns_on_exit": 1,
      "enter_condition": lambda emotion, event, removed_tasks, active_tasks_list: (not any(x.get_name() == "investigate emotion caused by event '{}'" for x in active_tasks_list) and
                                                                     not any(x.get_identifier() == "investigate emotion caused by event '{}'".format(event) for x in removed_tasks)), 
      "expires_after": math.inf, 
      "dag": {
          "ask_event_feelings": {
              "question": "say that it's important to confront our negative feelings and understand them fully, so you would like to ask again and in detail how the event {} makes them feel. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions apart from this.",
              "continue_condition": lambda bot_turn, user_turn: "ask_more_feelings" if (parsing_utils.is_answer(bot_turn, user_turn)) else "abort"
          },
          "ask_more_feelings": {
              "question": "ask, in the interest of self-discovery and self-awareness, if there are also other feelings associated with the event {}. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions apart from this.",
              "continue_condition": lambda bot_turn, user_turn: "end" if (parsing_utils.is_answer(bot_turn, user_turn)) else "abort"
           },
         }, 
      },
  "project {} emotion": { 
      "type": "emotion",
      "priority": 4, 
      "wait_turns_on_exit": 1,
      "enter_condition": lambda emotion, event, removed_tasks, active_tasks_list: (not any(x.get_identifier() == "project {} emotion".format(emotion) for x in active_tasks_list + removed_tasks)), 
      "expires_after": math.inf, 
      "dag": {
          "project": {
              "question": "ask the following question (you may paraphrase it slightly): Could you try to project your current {} feeling onto your childhood self?'. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions or say anything else after this.",
              "continue_condition": lambda bot_turn, user_turn: "end" if (parsing_utils.is_answer(bot_turn, user_turn)) else "abort"
           },
         }, 
      },
  "exercise recommendation": {
      "type": "emotion",
      "priority": 5, 
      "wait_turns_on_exit": 0,
      "enter_condition": lambda emotion, event, removed_tasks, active_tasks_list: (not any(x.get_identifier() == "exercise recommendation" for x in active_tasks_list)), 
      "expires_after": math.inf, 
      "dag": {
          "propose_exercise": {
              "question": "ask the following question (you may paraphrase it slightly): 'Would you like me to recommend a Self-Attachment technique exercise that might help?'",
              "continue_condition": lambda bot_turn, user_turn: "exercise_choice" if (parsing_utils.is_answer(bot_turn, user_turn) and parsing_utils.is_answer_positive(bot_turn, user_turn)) else "abort"
          },
          "exercise_choice": {
              "question": "ask the following question (you may paraphrase it slightly): 'I can recommend the following exercises, please let me know which one you would like'.",
              "continue_condition": lambda bot_turn, user_turn: "exercise_instructions" if (parsing_utils.is_answer(bot_turn, user_turn) and parsing_utils.wants_exercise(bot_turn, user_turn)) else "abort"
           },
           "exercise_instructions": {
              "question": "ask the following question (you may paraphrase it slightly): 'Please go to the exercise now, and let me know once you have done it. If for any reason you cannot do it right now, just let me know'.",
              "continue_condition": lambda bot_turn, user_turn: "end"
           },
         }, 
      },
}


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

  def execute_task(self, messages, exercises, prompt, available_tasks, active_tasks, removed_tasks, global_emotions_map, global_events_map):
    end_conversation = False
    continue_task = True

    reference_to_pass = ""
    if self.turns_since_added > 0:
      reference_to_pass = self.reference

    current_turn = list(self.dag.keys())[0]

    while continue_task and not end_conversation: #and self.pointer < len(self.dag):
        bot_turn, user_turn, messages, exercises, active_tasks, end_conversation = turn(self.dag[current_turn]["question"], reference_to_pass, messages, exercises, prompt, available_tasks, active_tasks, removed_tasks, global_emotions_map, global_events_map)
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

    return messages, exercises, active_tasks, end_conversation, removed_tasks


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


def add_microtasks(emotions_map, events_map, available_tasks, active_tasks, removed_tasks):
  for mt in available_tasks:
    if mt.get_type() == "emotion":
      for emotion in emotions_map:
        event = ""
        active_tasks, active_tasks_list = listify_queue(active_tasks, False)
        enter_condition = mt.get_enter_condition()(emotion, event, removed_tasks, active_tasks_list)
        if enter_condition: 
          active_tasks = add_to_queue(mt, emotion, active_tasks)
          print(f"Added microtask: {mt.get_name().format(emotion)}")
    elif mt.get_type() == "event":
      for event in events_map:
        emotion = ""
        active_tasks, active_tasks_list = listify_queue(active_tasks, False)
        enter_condition = mt.get_enter_condition()(emotion, event, removed_tasks, active_tasks_list)
        if enter_condition:
          active_tasks = add_to_queue(mt, event, active_tasks)
          print(f"Added microtask: {mt.get_name().format(event)}")
  return active_tasks


def load_microtasks():
  available_microtasks = []
  for key in mt_attributes:
    available_microtasks.append(Microtask(key))
  return available_microtasks


def turn(question, task_reference, messages, sat_exercises, prompt, available_tasks, all_tasks, removed_tasks, global_emotions_map, global_events_map):
  if question:
    messages.append({"role": "system", "content": f"{prompt}" + question.format(task_reference)})
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
     )
  bot_turn = api_response['choices'][0]['message']['content']
  print(colorama.Style.RESET_ALL)
  print(colorama.Back.WHITE + colorama.Fore.BLACK + f"MiTa: {bot_turn}")
  if question == "Paraphrase the following text, preserving its original meaning: 'I can recommend the following exercises, please let me know which one you would like:'. Do not ask any question or say anything else after this.":
    sat_utils.show_recommendations(sat_exercises)
  print(colorama.Back.WHITE + colorama.Fore.BLACK)
  user_turn = input(f'{username}: ')
  print(colorama.Style.RESET_ALL)
  global_emotions_map, global_events_map, emotions_map, events_map, sat_exercises = parsing_utils.parse_user_message(global_emotions_map, global_events_map, user_turn, sat_exercises)
  end = parsing_utils.wants_to_end(user_turn)
  
  if not question:
    all_tasks = add_microtasks(emotions_map, events_map, available_tasks, all_tasks, removed_tasks)
  else:
    del messages[-1]

  messages.append({"role": "assistant", "content": bot_turn})
  messages.append({"role": "user", "content": user_turn})

  return bot_turn, user_turn, messages, sat_exercises, all_tasks, end





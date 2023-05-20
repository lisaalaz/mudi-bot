import math

import parsing_utils


mt_attributes = {
  "none": {
    "type": "none",
    "priority": math.inf,
    "wait_turns_on_exit": 0,
    "enter_condition": lambda s_intention, emotion, event, removed_tasks, active_tasks_list, current_task: False,
    "expires_after": 0,
    "dag": {},
  },
  "suggest helplines": {
      "type": "intention",
      "priority": 0, 
      "wait_turns_on_exit": lambda removed_tasks: math.ceil(len(removed_tasks)/len(mt_attributes)),
      "enter_condition": lambda s_intention, emotion, event, removed_tasks, active_tasks_list, current_task: s_intention==True and (not (any(x.get_name()=="suggest helplines" for x in active_tasks_list)) and
                                                                                                                                    current_task.get_name()!="suggest helplines"),
      "expires_after": math.inf, 
      "dag": {
          "confirm_location": {
              "question": "say the following, without changing its meaning or asking any further questions: From what you just told me, I sensed that you might be feeling suicidal. I just want to pause for a moment and check on you. There is help available, please do talk to someone about your concerns and how you're feeling. You deserve to be listened to if you're going through a difficult time. In order to recommend some resources and phone numbers you can call right away, could you please tell me what country you are located in right now?",
              "continue_condition": lambda bot_turn, user_turn, active_tasks_list, current_task: "wait" if any(x.get_priority() < current_task.get_priority() for x in active_tasks_list) else (
                                                                                                                                   "list_helplines" if parsing_utils.is_answer(bot_turn, user_turn) else "abort"),
          },
          "list_helplines": {
              "question": "say the following, without changing its overall meaning: 'Here is a list of helplines for your location that you can call right away'",
              "continue_condition": lambda bot_turn, user_turn, active_tasks_list, current_task: "end" if parsing_utils.is_answer(bot_turn, user_turn) else "abort",
           },
         }, 
      },
  "investigate event causing {} emotion": {
      "type": "emotion",
      "priority": 1, 
      "wait_turns_on_exit": lambda removed_tasks: math.ceil(len(removed_tasks)/len(mt_attributes)),
      "enter_condition": lambda s_intention, emotion, event, removed_tasks, active_tasks_list, current_task: s_intention==False and (parsing_utils.is_emotion_negative(emotion) and (len(active_tasks_list) == 0 or
                                                                                                    (not any(x.get_name()=="investigate event causing {} emotion" for x in active_tasks_list + removed_tasks) and
                                                                                                        current_task.get_name()!="investigate event causing {} emotion"))),
      "expires_after": math.inf, 
      "dag": {
          "ask_event": {
              "question": "ask if something happened or if this is just a general feeling",
              "continue_condition": lambda bot_turn, user_turn, active_tasks_list, current_task: "wait" if any(x.get_priority() < current_task.get_priority() for x in active_tasks_list) else (
                                                                          "ask_what_happened" if (parsing_utils.is_answer(bot_turn, user_turn) and parsing_utils.is_specific(bot_turn, user_turn)) else "abort"),
          },
          "ask_what_happened": {
              "question": "ask if they would like to talk more about what happened",
              "continue_condition": lambda bot_turn, user_turn, active_tasks_list, current_task: "end" if parsing_utils.is_answer(bot_turn, user_turn) else "abort",
           },
         }, 
      },
  "investigate event '{}'": {
      "type": "event",
      "priority": 2, 
      "wait_turns_on_exit": lambda removed_tasks: math.ceil(len(removed_tasks)/len(mt_attributes)),
      "enter_condition": lambda s_intention, emotion, event, removed_tasks, active_tasks_list, current_task: s_intention==False and (len(active_tasks_list) == 0 or (not (any(x.get_name() == "investigate event '{}'" for x in active_tasks_list + removed_tasks)) and
                                                                                                   current_task.get_name()!="investigate event '{}'")),
      "expires_after": math.inf, 
      "dag": {
          "ask_when_event_happened": {
              "question": "ask when did this happen",
              "continue_condition": lambda bot_turn, user_turn, active_tasks_list, current_task: "end" if (parsing_utils.is_answer(bot_turn, user_turn)) else "abort",
           },
         }, 
      },
  "investigate emotion caused by event '{}'": {
      "type": "event",
      "priority": 3, 
      "wait_turns_on_exit": lambda removed_tasks: math.ceil(len(removed_tasks)/len(mt_attributes)),
      "enter_condition": lambda s_intention, emotion, event, removed_tasks, active_tasks_list, current_task: s_intention==False and (len(active_tasks_list) == 0 or
                                                               (not (any(x.get_name() == "investigate emotion caused by event '{}'" for x in active_tasks_list + removed_tasks)) and
                                                                    current_task.get_name()!="investigate emotion caused by event '{}'")),
                                                                                   
      "expires_after": math.inf, 
      "dag": {
          "ask_event_feelings": {
              "question": "ask what emotions are they feeling as a result of this",
              "continue_condition": lambda bot_turn, user_turn, active_tasks_list, current_task: "wait" if any(x.get_priority() < current_task.get_priority() for x in active_tasks_list) else (
                                                                                                                         "ask_more_feelings" if (parsing_utils.is_answer(bot_turn, user_turn)) else "abort"),
          },
          "ask_more_feelings": {
              "question": "ask if there are also other feelings right now",
              "continue_condition": lambda bot_turn, user_turn, active_tasks_list, current_task: "end" if (parsing_utils.is_answer(bot_turn, user_turn)) else "abort",
           },
         }, 
      },
  "project {} emotion": { 
      "type": "emotion",
      "priority": 4, 
      "wait_turns_on_exit": lambda removed_tasks: math.ceil(len(removed_tasks)/len(mt_attributes)),
      "enter_condition": lambda s_intention, emotion, event, removed_tasks, active_tasks_list, current_task: s_intention==False and (parsing_utils.is_emotion_negative(emotion) and (len(active_tasks_list) == 0 or
                                                                                                  (not (any(x.get_name() == "project {} emotion" for x in active_tasks_list + removed_tasks)) and
                                                                                                      current_task.get_name()!="project {} emotion"))),
      "expires_after": math.inf, 
      "dag": {
          "project": {
              "question": "ask 'can you try to project this feeling onto your childhood self?' (HINT: YOU MAY PARAPHRASE THIS QUESTION SLIGHTLY BUT YOU CANNOT ADD ANY MORE SENTENCES)",
              "continue_condition": lambda bot_turn, user_turn, active_tasks_list, current_task: "wait" if any(x.get_priority() < current_task.get_priority() for x in active_tasks_list) else (
                                                                                   "explain_projection" if (parsing_utils.is_question(user_turn)) else ("end" if parsing_utils.is_answer_positive(bot_turn, user_turn) else "abort")),
           },
           "explain_projection": {
              "question": "explain that to project a negative emotion onto the childhood self, one needs to imagine their childhood self is feeling what they are feeling right now, and console the child",
              "continue_condition": lambda bot_turn, user_turn, active_tasks_list, current_task: "end" if (parsing_utils.is_answer_positive(bot_turn, user_turn)) else "abort",
           }, 
         },
      },
  "exercise recommendation": {
      "type": "emotion",
      "priority": 5, 
      "wait_turns_on_exit": lambda removed_tasks: math.ceil(len(removed_tasks)/len(mt_attributes)),
      "enter_condition": lambda s_intention, emotion, event, removed_tasks, active_tasks_list, current_task: s_intention==False and ((not any(x.get_identifier() == "exercise recommendation" for x in active_tasks_list))), 
      "expires_after": math.inf, 
      "dag": {
          "propose_exercise": {
              "question": "ask 'Would you like a self-attachment technique exercise?' (HINT: YOU MAY PARAPHRASE THIS QUESTION SLIGHTLY BUT YOU CANNOT ADD ANY MORE SENTENCES)",
              "continue_condition": lambda bot_turn, user_turn, active_tasks_list, current_task: "wait" if any(x.get_priority() < current_task.get_priority() for x in active_tasks_list) else (
                                                                                         "exercise_choice" if (parsing_utils.is_answer_positive(bot_turn, user_turn)) else "abort"), #parsing_utils.is_answer(bot_turn, user_turn)
          },
          "exercise_choice": {
              "question": "say 'I can recommend the following exercises:' (HINT: YOU MAY PARAPHRASE THIS QUESTION SLIGHTLY BUT YOU CANNOT ADD ANY MORE SENTENCES)",
              "continue_condition": lambda bot_turn, user_turn, active_tasks_list, current_task: "wait" if any(x.get_priority() < current_task.get_priority() for x in active_tasks_list) else (
                                                                                         "exercise_instructions" if (parsing_utils.contains_number(user_turn) != "no number") else "abort"), #parsing_utils.is_answer(bot_turn, user_turn) 
           },
           "exercise_instructions": {
              "question": "say 'Please go through the exercise now and let me know once you are done, or if you cannot complete it for any reason' (HINT: YOU CAN PARAPHRASE THIS QUESTION BUT YOU CANNOT ADD ANY MORE SENTENCES)",
              "continue_condition": lambda bot_turn, user_turn, active_tasks_list, current_task: "end",
           },
         }, 
      },
}
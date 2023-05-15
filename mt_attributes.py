import math

import parsing_utils


mt_attributes = {
  "none": {
    "type": "none",
    "priority": math.inf,
    "wait_turns_on_exit": 0,
    "enter_condition": lambda emotion, event, removed_tasks, active_tasks_list, current_task: False,
    "expires_after": 0,
    "dag": {},
  },
  "investigate event causing {} emotion": {
      "type": "emotion",
      "priority": 1, 
      "wait_turns_on_exit": lambda removed_tasks: math.ceil(len(removed_tasks)/len(mt_attributes)),
      "enter_condition": lambda emotion, event, removed_tasks, active_tasks_list, current_task: parsing_utils.is_emotion_negative(emotion) and (len(active_tasks_list) == 0 or
                                                                                                    (not any(x.get_name()=="investigate event causing {} emotion" for x in active_tasks_list + removed_tasks) and
                                                                                                        current_task.get_name()!="investigate event causing {} emotion")),
      "expires_after": math.inf, 
      "dag": {
          "ask_event": {
              "question": {
                  "gpt-3.5-turbo": "ask what caused this {} feeling, or whether it is just a general feeling. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any further questions apart from this.",
                  "opt": "ask what caused this feeling or whether it is just a geneal feeling",
                  "DIAL-FLANT5-XL": "ask what caused this feeling or whether it is just a geneal feeling"
              },
              "continue_condition": lambda bot_turn, user_turn: "ask_what_happened" if (parsing_utils.is_answer(bot_turn, user_turn) and parsing_utils.is_specific(bot_turn, user_turn)) else "abort",
          },
          "ask_what_happened": {
              "question": {
                  "gpt-3.5-turbo": "ask if they can say a little more about what happened that caused the {} feeling. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions apart from this.",
                  "opt": "ask to talk some more about what happened that caused the {} feeling",
                  "DIAL-FLANT5-XL": "ask to talk some more about what happened that caused the {} feeling",
              },
              "continue_condition": lambda bot_turn, user_turn: "end" if parsing_utils.is_answer(bot_turn, user_turn) else "abort",
           },
         }, 
      },
  "investigate event '{}'": {
      "type": "event",
      "priority": 2, 
      "wait_turns_on_exit": lambda removed_tasks: math.ceil(len(removed_tasks)/len(mt_attributes)),
      "enter_condition": lambda emotion, event, removed_tasks, active_tasks_list, current_task: len(active_tasks_list) == 0 or (not (any(x.get_name() == "investigate event '{}'" for x in active_tasks_list + removed_tasks)) and
                                                                                                   current_task.get_name()!="investigate event '{}'"),
      "expires_after": math.inf, 
      "dag": {
          "ask_when_event_happened": {
              "question": {
                  "gpt-3.5-turbo": "ask when the event {} happened. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions apart from this.",
                  "opt": "ask when the event {} happened",
                  "DIAL-FLANT5-XL": "ask when the event {} happened",
              },
              "continue_condition": lambda bot_turn, user_turn: "end" if (parsing_utils.is_answer(bot_turn, user_turn)) else "abort",
           },
         }, 
      },
  "investigate emotion caused by event '{}'": {
      "type": "event",
      "priority": 3, 
      "wait_turns_on_exit": lambda removed_tasks: math.ceil(len(removed_tasks)/len(mt_attributes)),
      "enter_condition": lambda emotion, event, removed_tasks, active_tasks_list, current_task: len(active_tasks_list) == 0 or
                                                               (not (any(x.get_name() == "investigate emotion caused by event '{}'" for x in active_tasks_list + removed_tasks)) and
                                                                    current_task.get_name()!="investigate emotion caused by event '{}'"),
                                                                                   
      "expires_after": math.inf, 
      "dag": {
          "ask_event_feelings": {
              "question": {
                "gpt-3.5-turbo": "say that it's important to confront our negative feelings and understand them fully, so you would like to ask again and in detail how the event {} makes them feel. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions apart from this.",
                "opt": "ask in detail how the event {} makes them feel",
                "DIAL-FLANT5-XL": "ask in detail how the event {} makes them feel",
              },
              "continue_condition": lambda bot_turn, user_turn: "ask_more_feelings" if (parsing_utils.is_answer(bot_turn, user_turn)) else "abort"
          },
          "ask_more_feelings": {
              "question": {
                "gpt-3.5-turbo": "ask, in the interest of self-discovery and self-awareness, if there are also other feelings associated with the event {}. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions apart from this.",
                "opt": "ask if there are also other feelings associated with the event {}",
                "DIAL-FLANT5-XL": "ask if there are also other feelings associated with the event {}",
              },
              "continue_condition": lambda bot_turn, user_turn: "end" if (parsing_utils.is_answer(bot_turn, user_turn)) else "abort"
           },
         }, 
      },
  "project {} emotion": { 
      "type": "emotion",
      "priority": 4, 
      "wait_turns_on_exit": lambda removed_tasks: math.ceil(len(removed_tasks)/len(mt_attributes)),
      "enter_condition": lambda emotion, event, removed_tasks, active_tasks_list, current_task: parsing_utils.is_emotion_negative(emotion) and (len(active_tasks_list) == 0 or
                                                                                                  (not (any(x.get_name() == "project {} emotion" for x in active_tasks_list + removed_tasks)) and
                                                                                                      current_task.get_name()!="project {} emotion")),
      "expires_after": math.inf, 
      "dag": {
          "project": {
              "question": {
                  "gpt-3.5-turbo": "ask the following question (you may paraphrase it slightly) without adding any further sentences: Could you try to project your current {} feeling onto your childhood self?",
                  "opt": "ask to project their current {} feeling onto your childhood self",
                  "DIAL-FLANT5-XL": "ask to project their current {} feeling onto your childhood self",
              },
              "continue_condition": lambda bot_turn, user_turn: "explain_projection" if (parsing_utils.is_question(user_turn)) else ("end" if parsing_utils.is_answer_positive(bot_turn, user_turn) else "abort")
           },
           "explain_projection": {
              "question": {
                  "gpt-3.5-turbo": "explain that to project a negative emotion onto the childhood self, one needs to imagine their childhood self is feeling what they are feeling right now. Then they should picture themselves consoling and hugging the child, perhaps playing with them or singing a happy song.",
                  "opt":  "say that they need to imagine the childhood self is feeling the {} feeling and they are consoling the child",
                  "DIAL-FLANT5-XL": "say that they need to imagine the childhood self is feeling the {} feeling and they are consoling the child",
              },
              "continue_condition": lambda bot_turn, user_turn: "end" if (parsing_utils.is_answer_positive(bot_turn, user_turn)) else "abort",
           }, 
         },
      },
  "exercise recommendation": {
      "type": "emotion",
      "priority": 5, 
      "wait_turns_on_exit": lambda removed_tasks: math.ceil(len(removed_tasks)/len(mt_attributes)),
      "enter_condition": lambda emotion, event, removed_tasks, active_tasks_list, current_task: (not any(x.get_identifier() == "exercise recommendation" for x in active_tasks_list)), 
      "expires_after": math.inf, 
      "dag": {
          "propose_exercise": {
              "question": {
                  "gpt-3.5-turbo": "ask the following question (you may paraphrase it slightly): 'Would you like me to recommend a Self-Attachment technique exercise that might help?'",
                  "opt": "offer to suggest Self-Attachment technique exercise",
                  "DIAL-FLANT5-XL": "offer to suggest Self-Attachment technique exercise",
              },
              "continue_condition": lambda bot_turn, user_turn: "exercise_choice" if (parsing_utils.is_answer_positive(bot_turn, user_turn)) else "abort" #parsing_utils.is_answer(bot_turn, user_turn) and 
          },
          "exercise_choice": {
              "question": {
                  "gpt-3.5-turbo": "ask the following question in a respectful way (you may paraphrase it slightly) without adding any further sentences: I can recommend the following exercises, please let me know which one you would like.",
                  "opt": "Say that you can recommend the following exercises",
                  "DIAL-FLANT5-XL": "Say that you can recommend the following exercises",
              },
              "continue_condition": lambda bot_turn, user_turn: "exercise_instructions" if (parsing_utils.contains_number(user_turn) != "no number") else "abort" #parsing_utils.is_answer(bot_turn, user_turn) and 
           },
           "exercise_instructions": {
              "question": {
                  "gpt-3.5-turbo": "ask the following question in a respectful way (you may paraphrase it slightly) without adding any further sentences: Please go to the exercise now, and let me know once you have done it. If for any reason you cannot do it right now, just let me know.",
                  "opt": "Ask to begin the exercise and let you know once it's done, or if it cannot be done",
                  "DIAL-FLANT5-XL": "Ask to begin the exercise and let you know once it's done, or if it cannot be done",
              },
              "continue_condition": lambda bot_turn, user_turn: "end"
           },
         }, 
      },
}
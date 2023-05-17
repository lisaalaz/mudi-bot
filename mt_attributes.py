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
                  "opt": "ASKS WHAT CAUSED THIS FEELING"
                  "koala": "ASKS WHAT CAUSED THIS FEELING"
              },
              "continue_condition": lambda bot_turn, user_turn: "ask_what_happened" if (parsing_utils.is_answer(bot_turn, user_turn) and parsing_utils.is_specific(bot_turn, user_turn)) else "abort",
          },
          "ask_what_happened": {
              "question": {
                  "gpt-3.5-turbo": "ask if they can say a little more about what happened that caused the {} feeling. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions apart from this.",
                  "opt": "ASKS TO TALK MORE ABOUT WHAT HAPPENED",
                  "koala": "ASKS TO TALK MORE ABOUT WHAT HAPPENED",
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
                  "opt": "ASKS WHEN THIS HAPPENED",
                  "koala": "ASKS WHEN THIS HAPPENED",
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
                "opt": "ASKS WHAT EMOTIONS STEMMED FROM THIS EVENT",
                "koala": "ASKS WHAT EMOTIONS STEMMED FROM THIS EVENT",
              },
              "continue_condition": lambda bot_turn, user_turn: "ask_more_feelings" if (parsing_utils.is_answer(bot_turn, user_turn)) else "abort"
          },
          "ask_more_feelings": {
              "question": {
                "gpt-3.5-turbo": "ask, in the interest of self-discovery and self-awareness, if there are also other feelings associated with the event {}. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions apart from this.",
                "opt": "ASKS USER IF THEY ARE EXPERIENCING ANY OTHER FEELINGS",
                "koala": "ASKS USER IF THEY ARE EXPERIENCING ANY OTHER FEELINGS",
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
                  "opt": "IS AN INVITE TO PROJECT THIS FEELING ONTO THE CHILDHOOD SELF (hint: projecting a feeling onto the childhood self is a therapeutic practice)",
                  "koala": "IS AN INVITE TO PROJECT THIS FEELING ONTO THE CHILDHOOD SELF (hint: projecting a feeling onto the childhood self is a therapeutic practice)",
              },
              "continue_condition": lambda bot_turn, user_turn: "explain_projection" if (parsing_utils.is_question(user_turn)) else ("end" if parsing_utils.is_answer_positive(bot_turn, user_turn) else "abort")
           },
           "explain_projection": {
              "question": {
                  "gpt-3.5-turbo": "explain that to project a negative emotion onto the childhood self, one needs to imagine their childhood self is feeling what they are feeling right now. Then they should picture themselves consoling and hugging the child, perhaps playing with them or singing a happy song.",
                  "opt": "EXPLAINS THAT TO PROJECT A FEELING ONTO THE CHILDHOOD SELF ONE MUST IMAGINE THEIR CHILDHOOD SELF IS FEELING AS THEY DO NOW, AND TRY TO CONSOLE THE CHILD,",
                  "koala": "EXPLAINS THAT TO PROJECT A FEELING ONTO THE CHILDHOOD SELF ONE MUST IMAGINE THEIR CHILDHOOD SELF IS FEELING AS THEY DO NOW, AND TRY TO CONSOLE THE CHILD,",
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
                  "opt": "ASKS 'Would you like a self-attachment technique exercise?' (HINT: YOU CAN PARAPHRASE THIS QUESTION SLIGHTLY BUT YOU CANNOT ADD ANY MORE SENTENCES)",
                  "koala": "ASKS 'Would you like a self-attachment technique exercise?' (HINT: YOU CAN PARAPHRASE THIS QUESTION SLIGHTLY BUT YOU CANNOT ADD ANY MORE SENTENCES)",
              },
              "continue_condition": lambda bot_turn, user_turn: "exercise_choice" if (parsing_utils.is_answer_positive(bot_turn, user_turn)) else "abort" #parsing_utils.is_answer(bot_turn, user_turn) and 
          },
          "exercise_choice": {
              "question": {
                  "gpt-3.5-turbo": "ask the following question in a respectful way (you may paraphrase it slightly) without adding any further sentences: I can recommend the following exercises, please let me know which one you would like.",
                  "opt": "SAYS 'Ok, I can recommend the following exercises:' (HINT: YOU CAN PARAPHRASE THIS QUESTION SLIGHTLY BUT YOU CANNOT ADD ANY MORE SENTENCES)",
                  "koala": "SAYS 'Ok, I can recommend the following exercises:' (HINT: YOU CAN PARAPHRASE THIS QUESTION SLIGHTLY BUT YOU CANNOT ADD ANY MORE SENTENCES)",
              },
              "continue_condition": lambda bot_turn, user_turn: "exercise_instructions" if (parsing_utils.contains_number(user_turn) != "no number") else "abort" #parsing_utils.is_answer(bot_turn, user_turn) and 
           },
           "exercise_instructions": {
              "question": {
                  "gpt-3.5-turbo": "ask the following question in a respectful way (you may paraphrase it slightly) without adding any further sentences: Please go to the exercise now, and let me know once you have done it. If for any reason you cannot do it right now, just let me know.",
                  "opt": "SAYS 'Please go through the exercise now and let me know once you are done, or if you cannot complete it for any reason' (HINT: YOU CAN PARAPHRASE THIS QUESTION BUT YOU CANNOT ADD ANY MORE SENTENCES)",
                  "koala": "SAYS 'Please go through the exercise now and let me know once you are done, or if you cannot complete it for any reason' (HINT: YOU CAN PARAPHRASE THIS QUESTION BUT YOU CANNOT ADD ANY MORE SENTENCES)",
              },
              "continue_condition": lambda bot_turn, user_turn: "end"
           },
         }, 
      },
}
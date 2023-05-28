import math

task_attributes = {
  "none": {
    "priority": math.inf,
    "wait_turns_on_exit": 0,
    "expires_after": 0,
    "dag": {},
  },
  "suggest helplines": {
      "priority": 0, 
      #"wait_turns_on_exit": lambda finished_tasks: math.ceil(len(finished_tasks)/len(task_attributes)),
      "wait_turns_on_exit": 0,
      "expires_after": math.inf, 
      "dag": {
          "confirm_location": {
              "instruction": "say the following, without changing its meaning or asking any further questions: From what you just told me, I sensed that you might be feeling suicidal. I just want to pause for a moment and check on you. There is help available, please do talk to someone about your concerns and how you're feeling. You deserve to be listened to if you're going through a difficult time. In order to recommend some resources and phone numbers you can call right away, could you please tell me what country you are located in right now?",
          },
          "list_helplines": {
              "instruction": "if {user} indicated the country where they are located, give them a list of suicide helplines for their country that they can call right away. If instead {user} has not indicated a country or has clarified they are not suicidal, just answer whatever they said",
           },
         }, 
      },
  "investigate event causing negative emotion": {
      "priority": 1, 
      #"wait_turns_on_exit": lambda finished_tasks: math.ceil(len(finished_tasks)/len(task_attributes)),
      "wait_turns_on_exit": 0,
      "expires_after": 6, 
      "dag": {
          "ask_event": {
              "instruction": "ask if something happened or if this is just a general feeling",
          },
          "ask_what_happened": {
              "instruction": "if {user} indicated that something specific happened ask if they would like to talk more about it. Otherwise just answer whatever they said",
           },
         }, 
      },
  "investigate time of event": {
      "priority": 2, 
      #"wait_turns_on_exit": lambda finished_tasks: math.ceil(len(finished_tasks)/len(task_attributes)),
      "wait_turns_on_exit": 0,
      "expires_after": 8, 
      "dag": {
          "ask_when_event_happened": {
              "instruction": "ask when did this happen",
           },
         }, 
      },
  "investigate emotion caused by event": {
      "priority": 3, 
      #"wait_turns_on_exit": lambda finished_tasks: math.ceil(len(finished_tasks)/len(task_attributes)),
      "wait_turns_on_exit": 0,                                                                         
      "expires_after": 6, 
      "dag": {
          "ask_event_feelings": {
              "instruction": "ask what emotions are they feeling as a result of this",
          },
          "ask_more_feelings": {
              "instruction": "if {user} clearly indicated what emotions they are feeling, ask if there are also any other emotions that they can identify. Otherwise just answer whatever they said",
           },
         }, 
      },
  "project negative emotion": {
      "priority": 4, 
      #"wait_turns_on_exit": lambda finished_tasks: math.ceil(len(finished_tasks)/len(task_attributes)),
      "wait_turns_on_exit": 0,
      "expires_after": 10, 
      "dag": {
          "project": {
              "instruction": "ask 'can you try to project this feeling onto your childhood self?' (HINT: YOU MAY PARAPHRASE THIS QUESTION SLIGHTLY BUT YOU CANNOT ADD ANY MORE SENTENCES)",
           },
           "explain_projection": {
              "instruction": "if {user} asked how to do emotion projection or indicated they don't know how, explain that to project an emotion onto the childhood self, one needs to imagine their childhood self is feeling what they are feeling right now, and console the child. Otherwise just answer whatever they said",
           }, 
         },
      },
  "exercise recommendation": {
      "priority": 5, 
      #"wait_turns_on_exit": lambda finished_tasks: math.ceil(len(finished_tasks)/len(task_attributes)),
      "wait_turns_on_exit": 0,
      "expires_after": math.inf, 
      "dag": {
          "propose_exercise": {
              "instruction": "ask 'Would you like a self-attachment technique exercise?' (HINT: YOU MAY PARAPHRASE THIS QUESTION SLIGHTLY BUT YOU CANNOT ADD ANY MORE SENTENCES)",
          },
          "exercise_choice": {
              "instruction": "if {user} indicated they would like an exercise, present them with the following list of exercises: {exercise_list}. Just give them this list of exercises without explaining what they are or how to do them! If instead {user} indicated they do not want an exercise, just answer whatever they said",
           },
           "exercise_instructions": {
              "instruction": "if {user} indicated which exercise they would like, give them these instructions to complete it: {exercise_instructions} (hint: copy these instructions faithfully without adding anything to them). If instead {user} indicated they do not want an exercise or did not provide a number, just answer whatever they said",
           },
         }, 
      },
}
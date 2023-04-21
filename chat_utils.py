import colorama
import copy
import openai

from secret_key import key # You will need your own OpenAI API key to insert below
openai.api_key = key


EXERCISE_TITLES = [
            "0: None",
            "1: Recalling childhood memories",
            "2: Embracing and comforting the Child",
            "3: Singing a song of affection",
            "4: Expressing love and care for the Child",
            "5: Pledging to support and care for the Child",
            "6: Restoring our emotional world",
            "7: Maintaining a loving relationship with the Child and creating zest for life",
            "8: Enjoying nature",
            "9: Overcoming current negative emotions",
            "10: Overcoming past pain",
            "11: Muscle relaxation and playful face for intentional laughing",
            "12: Victory laughter on our own",
            "13: Laughing with our childhood self",
            "14: Intentional laughter",
            "15: Learning to change your perspective",
            "16: Learning to be playful about your past pains",
            "17: Identifying patterns of acting out personal resentments",
            "18: Planning more constructive actions",
            "19: Updating our rigid beliefs to enhance creativity",
            "20: Practicing Affirmations", #todo: check this
            "21: Recognizing and containing the internal persecutor",
            "22: Solving personal crises",
            "23: Discovering your true, free, and sovereign self in this age of emergency",
            ]

TITLE_TO_EXERCISE = {
            EXERCISE_TITLES[i]: i for i in range(len(EXERCISE_TITLES))
        }

EXERCISE_TEXTS = [
            ["None"],
            ["In a quiet place, look at your happy and unhappy photos. Recall positive and negative childhood memories and early relationships in the family."],
            [
                "2a:",
                  "(i) With your eyes closed, first imagine your happy photo/avatar, imagining that the child is near you.",
                  "(ii) now imagine you are embracing the child.",
                  "(iii) now imagine you are playing with the child, e.g. a game that you played as a child.",
                  "(iv) now imagine you are dancing with the child.",
                  "Reflect on how you feel in each phase from (i) to (iv).",
                "2b:",
                  "(i) With your eyes closed, imagine your unhappy photo/avatar, imagining the child is near you.",
                  "(ii) now imagine you are embracing and consoling the child.",
                  "(iii) Open your eyes, put on the Google Cardboard or and:",
                    "(a) Set a negative emotion (sad, angry, fearful or disgusted) on your avatar.",
                    "(b) Then click on Auto Emotion ” and by staring at your child avatar imagine you are reassuring and comforting your child which makes the child happy and eventually dance.",
                  "Reflect on how you feel in each phase from (i) to (iii).",
            ],
            ["Print copies of happy photo to display at home, work, and in your wallet. Consider setting its digital image as the background on your phone and laptop, etc. Select a jolly lyrical song you cherish that invokes feelings of warmth, affection, love. Learn the song by heart and sing it as often as you can in your daily routine. While looking at the happy photo/avatar, sing the song, as a way to establish a deep emotional bond with the child in your mind. Start quietly; then, over time, allow your voice to become louder while using more of your body (e.g. shaking your shoulders, hands, and lifting your eyebrows up and down). Imagine that in this way, like a parent, you are have a loving, passionate dialogue and are joyfully dancing and playing with the child."],
            ["While genuinely smiling at the happy photo/avatar, loudly say to your child: 'I passionately love you and deeply care for you'."],
            ["In this exercise, we start to care for the child as our own child. We attribute and project our own emotions to the child. We, as our adult self, begin with a pledge we make at an especial time and place. After reading the pledge silently, we confidently pledge out loud the following: 'From now on, I will seek to act as a devoted and loving parent to this child, consistently and wholeheartedly care for them in every way possible. I will do everything I can to support the health and emotional growth of this child'."],
            ["Through imagination or by drawing, consider your emotional world as a home with some derelict parts that you will fully renovate. The new home is intended to provide a safe haven at times of distress for the child and a safe base for the child to tackle life's challenges. The new home and its garden is bright and sunny; we imagine carrying out these self attachment exercises in this environment. The unrestored basement of the new house is the remnant of the derelict house and contains our negative emotions. When suffering negative emotions, imagine that the child is trapped in the basement but can gradually learn to open the door of the basement, walk out and enter the bright rooms, reuniting with the adult."],
            [
                "7a: Choose some short phrase, e.g., 'You are my beautiful child' or 'My love'. Say it slowly, out loud at least five times as you look at the happy photo/avatar. Then sing your favourite chosen love song at least five times. As previously, increase your volume and begin to use your whole body.",
                "7b: While looking in a mirror, imagine your image to be that of the Child (i.e., your emotional self), then begin to loudly sing your previously chosen song. As previously, increase your volume and begin to use your whole body. (If you find it difficult to imagine the Child in the mirror, put the 'Happy' photo of your Child in front of the mirror and do the exercise while looking at your Happy childhood photo in the mirror). Do this twice now and then as many times as possible in different circumstances during the day, such as while on the way to work or while cooking dinner, to integrate them into your new life. When singing your favourite song becomes a habit of yours, it becomes an effective tool for enhancing positive affects and managing emotions.",
            ],
            ["Creating an attachment to nature for your Child is an effective way to increase joy and reduce negative emotions. Go outside to a garden, local park, wood or forest. Spend at least 5 minutes admiring a tree, attempting to appreciate its real beauty as you have never previously experienced. Repeat this process, including with other aspects of nature (e.g. sky, stars, plants, birds, rivers, sea, your favourite animal), until you feel you have developed an attachment to nature that helps regulate your emotions. Achieving this will help you want to spend more time in nature after this course ends."],
            [
                "With closed eyes, imagine the unhappy photo/avatar and project your negative emotions to the unhappy photo/avatar representing the Child.",
                "While doing this:",
                "(i) loudly reassure the Child.",
                "(ii) give your face/neck/head a self massage.",
                "Repeat these steps until you are calmed and comforted.",
            ],
            [
                "With closed eyes, recall a painful childhood episode, such as emotional or physical abuse or loss of a significant figure, with all the details your still remember. Associate the face of the Child you were in the past with the selected unhappy photo/avatar. As you remember the associated emotions, e.g., helplessness, humiliation and rage, with closed eyes, imagine your Adult intervening in the scene like a good parent. ",
                "Imagine your Adult:",
                   "(i) approaching your Child quickly like any good parent with their child in distress.",
                   "(ii) loudly reassuring the Child that you have now come to save them, by standing up with a loud voice to any perpetrator, for example: 'Why are you hitting my Child?', and by supporting the Child with a loud voice, for example: 'My darling, I will not let them hurt you anymore'.",
                   "(iii) imaginatively cuddling your Child, by giving yourself a face/neck/head self-massage.",
                "Repeat (i), (ii), (iii) until comforted and soothed, acquiring mastery over the trauma.",
            ],
            ["For this exercise, try to act like a child: loosen up facial and body muscles, open up your mouth and sing your favourite song while laughing (or at least smiling) on your own."],
            ["Think of something you have accomplished today, e.g. doing household chores, having a conversation with a neighbour, or reading an article, and smile at the thought of this as an achievement, then once you are comfortable, begin to laugh for at least ten seconds."],
            ["Looking at your happy photo/avatar, smile and then begin to laugh for at least ten seconds. Repeat this process at least three times."],
            ["At a time when you are alone, open your mouth slightly, loosen your face muscles, raise your eyebrows, then slowly and continuously repeat one of the following tones, each of which uses a minimum amount of energy: 'eh, eh, eh, eh'; or 'ah, ah, ah, ah'; or 'oh, oh, oh, oh'; or 'uh, uh, uh, uh'; or 'ye, ye, ye, ye'. If you need a subject to laugh at, you can laugh at the silliness of the exercise! Once this continuous intentional laughter becomes a habit, you would be able to shape it according to your personality and style to create your own brand of laughter."],
            ["Stare at the black vase. Laugh or at least smile for one minute the moment your perception changes and you see two white faces, conceived as Adult and Child, looking at each other (IT, ST, PT). Stare at the two white faces and laugh or at least smile for one minute the moment your perception changes and you see the black vase (IT, ST)."],
            ["Visualize a painful event that took place in the past (it can be a recent event that you have struggled with, or a painful event that took place in your childhood and you have endured for a long time), and despite its painfulness, try to see a positive impact it has had for you. Use any of the theories for humour to try to laugh or at least smile at the event."],
            ["Try to identify any pattern of narcissistic and anti social feelings that your Child has acted out in your current or past relationships or any long term resentment borne against someone. Try to recognize how much of your time and energy is consumed in such acting out and bearing resentment."],
            [
                "Work out a new way to handle, in the future, what you have identified as acting out antisocial feelings or bearing personal resentment in your life.",
                "1. Without denying these feelings, try to reflect and contain them and avoid acting them out. Try to let go of the personal resentment. This may be hard and challenging but it is necessary for emotional growth. Here, you are taking a critical but constructive stance towards your Child and are exercising foresighted compassion.",
                "2. Find a positive way of re-channeling the aggressive energy invoked by these feelings into productive work (e.g., going for some exercise, talking to a friend, etc.) and ultimately into creative work towards your noble goal in life.",
            ],
            ["Challenge your usual ideological framework to weaken any one sided belief patterns and encourage spontaneity and examination of any issue from multiple perspectives. Practice this with subjects or themes that you have deep rooted beliefs about and you are also interested in. This may include any social, political, or ethical issue, such as marriage, sexual orientation or racism. For example, whatever your political viewpoint on a specific subject is, consider the subject both from a liberal and conservative or from a left wing and right wing point of view and try to understand both sides of the issue and challenge your dominant ideological framework. This does not mean that you would change your viewpoint but it allows you to see the subject from different perspectives and to be able to put yourself in other people's shoes. Try to consider a question or issue that is different from what you may have thought of while practising this exercise in the past, and do so for at least 5 minutes."],
            ["Put together a list of inspirational affirmations by figures you admire. Choose the three that inspire you most. Read them out and repeat slowly for at least three minutes."],
            [
                "The Adult becomes aware of the facets of the trauma triangle: internal persecutor, victim, and rescuer.",
                "The Adult examines the effects of this triangle (narcissism and lack of creativity) in daily life and previous experiences.",
                "The Adult reviews their important life experiences and their social and political points of view as an adult, with awareness how the internal persecutor operates.",
                "The Adult creates a list of examples from their own experiences for the four different ways the internal persecutor operates.",
                "The Adult carefully analyzes their life experiences for examples of being drawn to trauma, being traumatized by the internal persecutor, and projecting the internal persecutor onto others.",
                "Based on the above, the Adult re evaluates their experiences, contains the internal persecutor, victim mentality and blame games, allowing the development of creativity.",
            ],
            [
                "After the Child's arousal level is reduced and as we continue to practice the exercise for modulating negative affects, and the exercises for laughter, we ask our child the following:",
                "- How can you see the crisis as a way of becoming stronger? (hah hah hah).",
                "- How can you interpret the crisis as a way of reaching your noble goal? (hah hah hah).",
                "- Has the internal persecutor been projecting onto others again?",
                "The Adult asks the following questions:",
                "- What is the similarity between this crisis and ones I have faced before?",
                "- How is it similar to the family crisis I experienced as a child?",
                "- Aren't the other person's positive attributes greater than their negative ones?",
                "- How would a mature person interpret the crisis in comparison to my Child?",
                "- Can I see it from the perspective of the other?",
                "- Can I put myself in their place and understand their affects?",
                "- Given my new insights can I find a way to calm the people involved in the crisis so we can find a better solution for it?",
                "- If I cannot, can I just respectfully maintain my distance and end the argument/conflict?",
            ],
            [
                "Our Adult asks our Child if it makes any sense to be subservient to the super profit making system which has brought us to the present abyss.",
                "Do I really need all these desired products, objects and services following the myriad of messages and peer/societal pressures on me?",
                "Does it make sense to crave for a materialistic/hedonistic and selfish lifestyle when life is under the impending threat of destruction?",
                "Do we want to continue to play this zero sum materialistic game or do we want to follow our noble goals in tackling our existential problems?",
                "Can we save the living planet other than by working towards a new global social contract based on universal compassion in which human aggression can be sublimated to creativity for the common good?",
            ],
        ]

EXERCISE_RANKINGS = {
            0: EXERCISE_TITLES[9], #overcoming negative emotion
            1: EXERCISE_TITLES[10], #overcoming past pain
            2: EXERCISE_TITLES[7], #sing a song
            3: EXERCISE_TITLES[16], #learning to be playful about your past pain
            4: EXERCISE_TITLES[15], #learning to change your perspective
            5: EXERCISE_TITLES[17], #identifying patterns of acting out personal resentments
            6: EXERCISE_TITLES[18], #planning more constructive actions

            # The rest should just be recommended in numerical order.
        }

exercises = [i for i in range(1, 27)]

USERNAME = "Lisa"

EMOTIONS_MAP = {}
  # structure:
  # {emotion: {
  #    "intensity": str,
  #    "cause": str,   
  #    }
  # }

EVENTS_MAP = {}
  # structure:
  # {event: {
  #    "time_of_event": str,
  #    "resulting_emotion": str,
  #    }
  # }

MT_PRIORITIES = {
    "investigate event causing {} emotion": 0,
    "investigate event '{}'": 1,
    "investigate emotion caused by event '{}'": 2,
    "project {} emotion": 3,
    "exercise recommendation": 4,
    }

def add_exercises(emotion, exercises):
  if is_emotion_negative(emotion) == "no":
    exercises.extend([EXERCISE_TITLES[15], EXERCISE_TITLES[17], EXERCISE_TITLES[18],
                          EXERCISE_TITLES[7], EXERCISE_TITLES[8], EXERCISE_TITLES[12], 
                          EXERCISE_TITLES[13], EXERCISE_TITLES[14], EXERCISE_TITLES[19],
                          EXERCISE_TITLES[21], EXERCISE_TITLES[22], EXERCISE_TITLES[23],
                          EXERCISE_TITLES[26]])
  else:
    if emotion in ["jealousy", "envy", "anger"]:
      exercises.extend([EXERCISE_TITLES[17], EXERCISE_TITLES[18]])
    else:
      exercises.extend([EXERCISE_TITLES[9], EXERCISE_TITLES[7], EXERCISE_TITLES[16], EXERCISE_TITLES[15]])
  exercises = list(set(exercises))
  return exercises

def give_exercise_instructions(exercise_number):
  for line in EXERCISE_TEXTS[exercise_number]:
    print(line)

def drop_existing_keys(dict1, dict2):
  new_dict = copy.deepcopy(dict1)
  for key in dict1:
    if key in dict2:
      del new_dict[key]
  return new_dict


def is_answer(question, reply):
  # Whether user's reply answers bot's utterance or not.
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Given utterance_A: {question} and utterance_B: {reply}, does utterance_B answer utterance_A? Answer yes or no."}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "yes" in answer.lower():
    answer = "yes"
  else:
    answer = "no"
  #print(f"Is answer: {answer}")
  return answer

def is_question(text):
  # Established whether the user's utterance contains a question for the bot to answer.
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Does the following sentence contain a question (answer only yes or no): {text}"}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "yes" in answer.lower():
    answer = "yes"
  else:
    answer = "no"
  #print(f"Is question: {answer}")
  return answer

def is_answer_positive(question, reply):
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Person_A: {question} Person_B: {reply}. Did Person_B answer 'yes' or 'no' to Person_A's question? Just say yes or no."}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "yes" in answer.lower():
    answer = "yes"
  else:
    answer = "no"
  #print(f"is answer positive: {answer}")
  return answer

def specific_or_general(question, reply):
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Person_A: {question} Person_B: {reply}. Did Person_B answer that something specific caused the feeling or that it's just a general feeling? Just say specific or general."}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "specific" in answer.lower():
    answer = "specific"
  else:
    answer = "general"
  #print(f"cause of feeling: {answer}")
  return answer

def event_classification(text):
  # Whether user's utterance describes an event, and whether it is personal or not.
  is_event = False
  personal_or_impersonal = ""
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"[Input]: My cat died last week. [Is it an event and is it personal]: yes, personal. [Input]: I had a terrible fight with my sister and I am sad now. [Is it an event and is it personal]: yes, personal. [Input]: Joe Biden has won the election. [Is it an event and is it personal]: yes, not personal. [Input]: I went to cemetery the other day, to visit my father's grave. He died a long time ago. [Is it an event and is it personal]: yes, personal. [Input]: I hope I can find a boyfriend. [Is it an event and is it personal]: no, not an event. [Input]: The Mets are playing a match tomorrow. [Is it an event and is it personal]: yes, not personal. [Input]: I am quite sad. [Is it an event and is it personal]: no, not an event. [Input]: Everyone is becoming stupid in this country. [Is it an event and is it personal]: yes, not personal. [Input]: {text}. [Is it an event and is it personal]:"}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "yes" in answer.lower():
    is_event = "yes"
  else:
    is_event = "no"
  if "impersonal" in answer.lower():
    personal_or_impersonal = "impersonal"
  elif "personal" in answer.lower():
    personal_or_impersonal = "personal"
  #print(f"is event: {is_event}, {personal_or_impersonal}")
  return is_event, personal_or_impersonal 

def extract_event(text):
  # Extracts very short summary of described event.
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Input: My cat died last week. Summary: {USERNAME}'s cat died. Input: I had a terrible fight with my sister and I am sad now. Summary: {USERNAME} had a fight with their sister. Input: I went to cemetery the other day, to visit my father's grave. He died a long time ago. Summary: {USERNAME} went to the cemetery. Input: {text}. Summary:"}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  #print(f"Extracted event: {answer}")
  return answer

def past_or_future_event(text):
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Is the main event described in the following text in the past or the future: {text}. Answer only the word 'past' or 'future'."}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "future" in answer.lower():
    answer = "future"
  else:
    answer = "past"
  #print(f"Past or future event: {answer}")
  return is_answer

def recent_or_distant_event(text):
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Classify the event described in the following text as recent or distant: {text}. Distant events are those that happened 10 years ago or more. Just answer recent or distant. If there is no indication of time, answer unknown."}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "distant" in answer.lower():
    answer = "distant"
  else:
    answer = "recent"
  #print(f"Recent or distant event: {answer}")
  return answer

def is_emotion(text):
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"[Input]: My cat died last week. [Does it express an emotion]: no. [Input]: I had a terrible fight with my sister and I am sad now. [Does it express an emotion]: yes. [Input]: Yes thank you. [Does it express an emotion]: no. [Input]: Joe Biden has won the election. [Does it express an emotion]: no. [Input]: I went to cemetery the other day, to visit my father's grave. He died a long time ago. [Does it express an emotion]: no. [Input]: I love my boyfriend. [Does it express an emotion]: yes. [Input]: Hey how are you? [Does it express an emotion]: no. [Input]: The Mets are playing a match tomorrow. [Does it express an emotion]: no. [Input]: I am quite anxious. [Does it express an emotion]: yes. [Input]: Everyone is becoming stupid in this country. [Does it express an emotion]: no. [Input]: Ok. [Does it express an emotion]: no. [Input]: {text}. [Does it express an emotion]:"}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "yes" in answer.lower():
    answer = "yes"
  else:
    answer = "no"
  #print(f"expresses emotion: {answer}")
  return answer

def emotion_classification(text):
  emotions_list = ["happiness", "contentment", "sadness", "fear", "anxiety", "anger", "love", "insecurity", "disgust", "disappointment", "shame", "guilt", "envy", "jealousy"]
  emotion = "neutral"
  degree = ""
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Out of the following emotions: {', '.join(emotions_list)}, which of these emotions is expressed in the following text, and how intense is it, out of low, medium or high? Just state the intensity and the emotion name, for example 'high sadness': {text}"}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  for emo in emotions_list:
      if emo in answer.lower():
        emotion = emo
  for d in ["low", "medium", "high"]:
      if d in answer.lower():
        degree = d
  #print(f"emotion found: {emotion}, {degree}")
  return emotion, degree

def is_emotion_negative(emotion):
  answer = "yes"
  if emotion.lower() in ["happiness", "contentment", "love", "neutral"]:
    answer = "no"
  #print(f"is emotion negative: {answer}")
  return answer

def contains_number(text):
  if "1" in text:
    answer = "1"
  elif "2" in text:
    answer = "2"
  elif "3" in text:
    answer = "3"
  elif "4" in text:
    answer = "4"
  else:
    api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Write the number, in digits, identified in the following text. Write the number and nothing else (no punctuation). If the answer does not contain a number at all, just say 'no number': {text}"}
        ]
     )
    answer = api_response['choices'][0]['message']['content']
  #print(f"contains number: {answer}")
  return answer

def wants_exercise(question, answer):
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"Speaker_A: {question}. Speaker_B: {answer}. Does Speaker_B want to do an exercise? Answer yes or no."}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "yes" in answer.lower():
    answer = "yes"
  else:
    answer = "no"
  #print(f"user wants exercise: {answer}")
  return answer

def wants_to_end(text):
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
             "content": f"does speaker of the following utterance imply that they wish to end the conversation (say just yes or no): {text}"}
        ]
     )
  answer = api_response['choices'][0]['message']['content']
  if "yes" in answer.lower():
    answer = True
  else:
    answer = False
  #print(f"user wants to end conversation: {answer}")
  return answer

def parse_user_message(exercises, prompt):
  emotions_map = {}
  events_map = {}

  is_event, _ = event_classification(prompt)
  emotion_detected = is_emotion(prompt)

  if emotion_detected == "yes":
    emotion, degree = emotion_classification(prompt)
    exercises = add_exercises(emotion_detected, exercises)
  else:
    emotion, degree = ("", "")

  if is_event == "yes":
    event_summary = extract_event(prompt)
    events_map[event_summary] = {}
    #if past_or_future_event(prompt) == "past":
    event_time = recent_or_distant_event(prompt)
    events_map[event_summary]["time_of_event"] = event_time
    if emotion_detected == "yes" and emotion != "neutral":
        events_map[event_summary]["resulting_emotion"] = emotion
        emotions_map[emotion] = {}
        emotions_map[emotion]["intensity"] = degree
        emotions_map[emotion]['cause'] = event_summary
    else:
        events_map[event_summary]["resulting_emotion"] = None
  elif emotion_detected == "yes" and emotion != "neutral":
      emotions_map[emotion] = {}
      emotions_map[emotion]["intensity"] = degree
      emotions_map[emotion]['cause'] = None

  emotions_map = drop_existing_keys(emotions_map, EMOTIONS_MAP)
  events_map = drop_existing_keys(events_map, EVENTS_MAP)

  EMOTIONS_MAP.update(emotions_map)
  EVENTS_MAP.update(events_map)

  return emotions_map, events_map, exercises

class Microtask():
  def __init__(self, task_name, reference, exit_condition):
    #class attributes
    self.identifier = task_name.format(reference)
    self.priority = MT_PRIORITIES[task_name]
    self.expires_after = 10
    self.n_turns = len(MT_LISTS[task_name])
    self.exit_condition = exit_condition
    self.wait_turns_on_exit = 2
    self.dag = MT_LISTS[task_name]

    #instance attributes
    self.args = {
        "reference": reference,
        "pointer": 0,
        "is_active": True,
        "turns_since_active": 0,
    }

  def get_identifier(self):
    return self.identifier

  def get_priority(self):
    return self.priority

  def get_n_turns(self):
    return self.n_turns

  def exit(self):
    self.args["is_active"] = False

  def get_all_args(self):
    return self.args

  def get_arg(self, arg):
    return self.args[arg]

  def move_pointer_forward(self):
    self.args["pointer"] += 1

  def increase_turn_counter(self):
    self.args["turns_since_active"] += 1

  def print_statement(self):
    print(f"Added microtask: {self.identifier}...")

  def remove_task(self, active_tasks, removed_tasks):
    active_tasks.remove(self)
    removed_tasks.append(self.identifier)
    return active_tasks, removed_tasks

  def execute_task(self, messages, exercises, prompt, active_tasks, removed_tasks):
    continue_task = True
    end_conversation = False
    removed = False
    i = 0
    #reference_to_pass = ""
    #if self.args["turns_since_active"] > 0:
    reference_to_pass = self.args["reference"]
    while i < len(self.dag) and continue_task and not end_conversation:
      messages, exercises, active_tasks, continue_task, end_conversation = self.dag[i](reference_to_pass, messages, exercises, prompt, active_tasks, removed_tasks)
      self.move_pointer_forward()
      self.increase_turn_counter()
      if not continue_task or end_conversation:
        active_tasks, removed_tasks = self.remove_task(active_tasks, removed_tasks)
        removed = True
        print(f"Aborted microtask: {self.get_identifier()}")
      i += 1
      
    if i == len(self.dag):
      if self in active_tasks:
        active_tasks, removed_tasks = self.remove_task(active_tasks, removed_tasks)
        removed = True
        print(f"Completed microtask: {self.get_identifier()}")
    return messages, exercises, active_tasks, end_conversation, removed, removed_tasks

def add_microtasks(emotions_map, events_map, microtasks, removed_tasks):
  new_microtasks = []

  for emotion in emotions_map:
    if is_emotion_negative(emotion):
      if not any(x[:19] == "investigate event c" for x in removed_tasks) and not any(x.get_identifier()[:19] == "investigate event c" for x in microtasks):
        new_microtasks.append(Microtask(
          task_name="investigate event causing {} emotion",
          reference=emotion,
          exit_condition=(is_emotion_negative(emotion) == "no" or any(x["resulting_emotion"] == emotion for x in events_map.values())),   
        ))
      if "project {} emotion".format(emotion) not in removed_tasks and not any(x.get_identifier()[:7] == "project" for x in microtasks):
        new_microtasks.append(Microtask(
          task_name="project {} emotion",
          reference=emotion,
          exit_condition=(is_emotion_negative(emotion) == "no"),
        ))
    if not any(x.get_identifier() == "exercise recommendation" for x in microtasks):
      new_microtasks.append(Microtask(
        task_name="exercise recommendation",
        reference=emotion,
        exit_condition=False,
      ))
  for event in events_map:
    if not any(x.get_identifier()[:19] == "investigate event '" for x in microtasks) and not any(x[:19] == "investigate event '" for x in removed_tasks):
      #if "investigate event '{}'".format(event) not in removed_tasks:
        new_microtasks.append(Microtask(
          task_name="investigate event '{}'",
          reference=event,
          exit_condition=(events_map[event]["time_of_event"]),
        ))
    if not any(x.get_identifier()[:19] == "investigate emotion" for x in microtasks):
      if "investigate emotion caused by event '{}'".format(event) not in removed_tasks:
       new_microtasks.append(Microtask(
         task_name="investigate emotion caused by event '{}'",
         reference=event,
         exit_condition=(events_map[event]["resulting_emotion"]),
       ))
  new_microtasks.sort(key=lambda x: x.priority)
  for mt in new_microtasks:
    mt.print_statement()

  microtasks = new_microtasks + microtasks
  microtasks.sort(key=lambda x: x.priority)
  return microtasks

def turn(question, task_reference, messages, exercises, prompt, all_tasks, removed_tasks):
  messages.append({"role": "system", "content": f"{prompt}" + question.format(task_reference)})
  api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
     )
  bot_turn = api_response['choices'][0]['message']['content']
  print(colorama.Back.BLUE + colorama.Fore.WHITE + f"MiTa: {bot_turn}")
  if question == "paraphrase the following text, preserving its original meaning and without adding anything to it: 'I can recommend the following exercises, please let me know which one you would like.'":
    for ex in exercises:
      print(ex)
  print(colorama.Back.WHITE + colorama.Fore.BLACK)
  user_turn = input(f'{USERNAME}: ')
  print(colorama.Style.RESET_ALL)
  emotions_map, events_map, exercises = parse_user_message(exercises, user_turn)
  all_tasks = add_microtasks(emotions_map, events_map, all_tasks, removed_tasks)
  end = wants_to_end(user_turn)

  del messages[-1]
  messages.append({"role": "assistant", "content": bot_turn})
  messages.append({"role": "user", "content": user_turn})

  return bot_turn, user_turn, messages, exercises, all_tasks, end

def free_turn(task_reference, messages, exercises, prompt, all_tasks, removed_tasks):
  api_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
          )
  bot_turn = api_response['choices'][0]['message']['content']
  messages.append({"role": "assistant", "content": bot_turn})
  print(colorama.Back.BLUE + colorama.Fore.WHITE + f"MiTa: {bot_turn}")
  print(colorama.Back.WHITE + colorama.Fore.BLACK)
  user_turn = input(f"{USERNAME}: ")
  print(colorama.Style.RESET_ALL)
  end_conversation = wants_to_end(user_turn)
  emotions_map, events_map, exercises = parse_user_message(exercises, user_turn)
  messages.append({"role": "user", "content": user_turn})
  all_tasks = add_microtasks(emotions_map, events_map, all_tasks, removed_tasks)

  return messages, exercises, all_tasks, True, end_conversation

def ask_event(task_reference, messages, exercises, prompt, all_tasks, removed_tasks):
    continue_task = True
    question = "ask what caused this {} feeling, or whether it is just a general feeling. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any further questions apart from this."
    bot_turn, user_turn, messages, exercises, all_tasks, end_conversation = turn(question, task_reference, messages, exercises, prompt, all_tasks, removed_tasks) 
    if is_answer(bot_turn, user_turn) == "yes":
      answer_type = specific_or_general(bot_turn, user_turn)
      if answer_type == "general":
        continue_task = False
      else:
        pass
    else:
      continue_task = False
    return messages, exercises, all_tasks, continue_task, end_conversation

def ask_what_happened(task_reference, messages, exercises, prompt, all_tasks, removed_tasks):
    continue_task = True
    question = "ask if they can say a little more about what happened that caused the {} feelings. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions apart from this."
    bot_turn, user_turn, messages, exercises, all_tasks, end_conversation = turn(question, task_reference, messages, exercises, prompt, all_tasks, removed_tasks) 
    if is_answer(bot_turn, user_turn) == "no":
      continue_task = False
    return messages, exercises, all_tasks, continue_task, end_conversation

def ask_when_event_happened(task_reference, messages, exercises, prompt, all_tasks, removed_tasks):
    continue_task = True
    question = "ask when the event {} happened. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions apart from this."
    bot_turn, user_turn, messages, exercises, all_tasks, end_conversation = turn(question, task_reference, messages, exercises, prompt, all_tasks, removed_tasks) 
    if is_answer(bot_turn, user_turn) == "yes":
      event_time = recent_or_distant_event(user_turn)
      if event_time == "distant":
        pass
      else:
        pass
    else:
      continue_task = False
    return messages, exercises, all_tasks, continue_task, end_conversation

def ask_event_feelings(task_reference, messages, exercises, prompt, all_tasks, removed_tasks):
    continue_task = True
    question = "say that it's important to confront our negative feelings and understand them fully, so you would like to ask again and in detail how the event {} makes them feel. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions apart from this."
    bot_turn, user_turn, messages, exercises, all_tasks, end_conversation = turn(question, task_reference, messages, exercises, prompt, all_tasks, removed_tasks) 
    if is_answer(bot_turn, user_turn) == "yes":
      if is_emotion(user_turn) == "yes":
        #emotion, degree = emotion_classification(user_turn)
        pass
      else:
        pass
    else:
      continue_task = False
    return messages, exercises, all_tasks, continue_task, end_conversation

def ask_more_feelings(task_reference, messages, exercises, prompt, all_tasks, removed_tasks):
    continue_task = True
    question = "apologise for being so insistent, and in the interest of self-discovery and self-awareness ask if there are also other feelings associated with the event {}. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions apart from this." #, apart from the main feeling already expressed. 
    bot_turn, user_turn, messages, exercises, all_tasks, end_conversation = turn(question, task_reference, messages, exercises, prompt, all_tasks, removed_tasks) 
    if is_answer(bot_turn, user_turn) == "yes":
      if is_emotion(user_turn) == "yes":
        #emotion, degree = emotion_classification(user_turn)
        pass
      else:
        pass
    else:
      continue_task = False
    return messages, exercises, all_tasks, continue_task, end_conversation

def project(task_reference, messages, exercises, prompt, all_tasks, removed_tasks):
    continue_task = True
    question = "ask the following question (you may paraphrase it slightly): Could you try to project your current {} feeling onto your childhood self?'. If you said the same thing previously, change this enough so it is not repetitive. Do not ask any other questions or say anything else after this."
    bot_turn, user_turn, messages, exercises, all_tasks, end_conversation = turn(question, task_reference, messages, exercises, prompt, all_tasks, removed_tasks) 
    if is_answer(bot_turn, user_turn) == "yes": 
      if is_question(user_turn) == "no":
        pass
      else:
        pass
    else:
      continue_task = False
    return messages, exercises, all_tasks, continue_task, end_conversation

def propose_exercise(task_reference, messages, exercises, prompt, all_tasks, removed_tasks):
    continue_task = True
    question = "paraphrase the following sentence, preserving its original meaning and without adding anything to it: 'would you like me to recommend a Self-Attachment technique exercise that might help?'"
    bot_turn, user_turn, messages, exercises, all_tasks, end_conversation = turn(question, task_reference, messages, exercises, prompt, all_tasks, removed_tasks) 
    if is_answer(bot_turn, user_turn) == "yes":
      answer_type = is_answer_positive(bot_turn, user_turn)
      if answer_type == "no":
        continue_task = False
      else:
        pass
    else:
      continue_task = False
    return messages, exercises, all_tasks, continue_task, end_conversation

def exercise_choice(task_reference, messages, exercises, prompt, all_tasks, removed_tasks):
    continue_task = True
    question = "paraphrase the following text, preserving its original meaning and without adding anything to it: 'I can recommend the following exercises, please let me know which one you would like.'"
    bot_turn, user_turn, messages, exercises, all_tasks, end_conversation = turn(question, task_reference, messages, exercises, prompt, all_tasks, removed_tasks) 
    number = contains_number(user_turn)
    user_intention = wants_exercise(bot_turn, user_turn)
    if is_answer(bot_turn, user_turn) == "yes":
      if "no number" in number.lower():
        if user_intention == "no":
          continue_task = False
        else:
          pass #should repeat the question and apologise for not understanding
    else:
      continue_task = False
    return messages, exercises, all_tasks, continue_task, end_conversation

def exercise_instructions(task_reference, messages, exercises, prompt, all_tasks, removed_tasks):
    continue_task = True
    question = "paraphrase the following text, preserving its original meaning or adding anything to it: 'Please go to the exercise now, and let me know once you have done it. If for any reason you cannot do it right now, just let me know.'"
    bot_turn, user_turn, messages, exercises, all_tasks, end_conversation = turn(question, task_reference, messages, exercises, prompt, all_tasks, removed_tasks) 
    return messages, exercises, all_tasks, continue_task, end_conversation

MT_LISTS = {
  "investigate event causing {} emotion": [ask_event, ask_what_happened, free_turn, free_turn],
  "investigate event '{}'": [ask_when_event_happened, free_turn],
  "investigate emotion caused by event '{}'": [ask_event_feelings, free_turn, ask_more_feelings, free_turn],
  "project {} emotion": [project, free_turn],
  "exercise recommendation": [propose_exercise, exercise_choice, exercise_instructions],
}

# Main chatbot function
def chatbot():
  prompt = "Answer what the user just said and answer any question they asked in full. After that, you should also "
  messages = [
      {"role": "system", 
       "content": f"Your name is MiTa, you are a kind and empathetic psychotherapist who wants to help the other person explore their emotions and feel better. You call the other person by their name: {USERNAME}. You have met {USERNAME} before. You are very supportive of {USERNAME}. When speaking about yourself, you always refer to yourself as a virtual therapist. You never ever say that you are a language model. You do not ever mention relaxation techniques, meditation, mindfulness, self-care practices, coping mechanisms, ways to manage the stress, breathing exercises or anything connected to these things. When {USERNAME} is distressed or something bad happened, all you do is ask questions in a supportive way and you can ask them if they want a Self-attachment exercise such as projecting a negative emotion onto their childhood self, but only when explicitly instructed to do so."},
       {"role": "user", 
       "content": "Hello MiTa"},
  ]
  exercises = []
  microtasks = []
  removed_tasks = []
  end_conversation = False

  while not end_conversation:
    for x in microtasks:
      x.increase_turn_counter()

    api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
      )
    bot_utterance = api_response['choices'][0]['message']['content']
    messages.append({"role": "assistant", "content": bot_utterance})
    print(colorama.Back.BLUE + colorama.Fore.WHITE + f"MiTa: {bot_utterance}")
    print(colorama.Back.WHITE + colorama.Fore.BLACK)
    prompt = input(f"{USERNAME}: ")
    print(colorama.Style.RESET_ALL)
    end_conversation = wants_to_end(prompt)
    emotions_map, events_map, exercises = parse_user_message(exercises, prompt)
    messages.append({"role": "user", "content": prompt})
    
    microtasks = add_microtasks(emotions_map, events_map, microtasks, removed_tasks)
  
    if microtasks:
      print(f"Current exercises: {exercises}")
      i = 0
      while i < len(microtasks):
        #if microtasks[i].get_arg("is_active"): # sanity check if mt is active
        current_mt = microtasks[i]
        print(f"Current active microtasks: {[x.get_identifier() for x in microtasks]}")#[x.get_identifier() for x in microtasks if x.get_arg('is_active')]
        print(f"Completed and aborted microtasks: {removed_tasks}")
        print(f"Executing microtask: {current_mt.get_identifier()}")
        messages, exercises, microtasks, end_conversation, removed, removed_tasks = current_mt.execute_task(messages, exercises, prompt, microtasks, removed_tasks)
        if not removed:
          i += 1
        
  if end_conversation:
    messages.append({"role": "system", 
       "content": f"{USERNAME} Needs to go now. Say goodbye to {USERNAME} and end the conversation until next time."})
    api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
      )
    bot_utterance = api_response['choices'][0]['message']['content']
    messages.append({"role": "assistant", "content": bot_utterance})
    print(colorama.Back.BLUE + colorama.Fore.WHITE + f"MiTa: {bot_utterance}")
    print(colorama.Style.RESET_ALL)
    print("--------CONVERSATION ENDED--------")
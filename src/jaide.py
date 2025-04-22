import spacy
import random
from transformers import AutoTokenizer, T5ForConditionalGeneration
from difflib import SequenceMatcher

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spacy model")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

class Jaide:
    def __init__(self):
        self.bot_name = "jaide"
        self.user_name = None
        self.user_info = {}
       
        ######### IMOPORTANT #########
        # IDGAF RN I will abstract these into JSON later LOL
        self.practice_topics = {
            "daily_routines": [
                "What time do you usually wake up in the morning?",
                "Can you describe your morning routine?",
                "What's your favorite meal of the day?",
                "How do you usually spend your evenings?",
                "What do you like to do on weekends?"
            ],
            "hobbies": [
                "What are your favorite hobbies?",
                "How often do you practice your hobbies?",
                "When did you start getting interested in your hobby?",
                "Would you like to try any new hobbies?",
                "Can you describe what you enjoy most about your favorite activity?"
            ],
            "travel": [
                "What's your favorite place you've visited?",
                "Where would you like to travel next?",
                "Do you prefer mountains, beaches, or cities when traveling?",
                "What's the most interesting food you've tried while traveling?",
                "How do you prepare for a trip?"
            ],
            "food": [
                "What's your favorite cuisine?",
                "Do you enjoy cooking at home?",
                "What dish are you best at preparing?",
                "Have you tried any new foods recently?",
                "What foods did you dislike as a child but enjoy now?"
            ],
            "learning_english": [
                "Why are you learning English?",
                "What's the most difficult part of English pronunciation for you?",
                "How long have you been studying English?",
                "What methods do you use to practice your English?",
                "What English sounds are most challenging for you?"
            ],
            "school_or_work": [
                "What do you do for work or school?",
                "What’s your favorite subject or part of your job?",
                "What does a typical day at school or work look like?",
                "Do you prefer working in a team or alone?",
                "Have you ever had a really interesting project?"
            ],
            "technology": [
                "How often do you use your phone or computer?",
                "What apps or websites do you use every day?",
                "Do you prefer texting or calling people?",
                "What’s your opinion on social media?",
                "Is there a new technology you’re excited about?"
            ],
            "weather": [
                "What’s the weather like today?",
                "Do you prefer hot or cold weather?",
                "What do you like to do on rainy days?",
                "Has it ever snowed where you live?",
                "How does the weather affect your mood?"
            ],
            "movies_and_tv": [
                "What’s your favorite movie or TV show?",
                "Who is your favorite actor or actress?",
                "Do you prefer comedies, dramas, or action films?",
                "Have you watched anything good recently?",
                "Do you like watching shows in English or your native language?"
            ],
            "music": [
                "What kind of music do you like?",
                "Who is your favorite singer or band?",
                "Do you play any musical instruments?",
                "When do you usually listen to music?",
                "Have you ever been to a concert?"
            ]
        }
        # whenever we extract a key word from user text
        self.topic_feedback_templates = {
            "travel": [
                "{}? That sounds like a fascinating destination!",
                "I've heard good things about {}.",
                "{} must have been an amazing place to visit!",
                "Visiting {} sounds like an adventure!"
            ],
            "food": [
                "{}? Yummy! That’s a delicious choice.",
                "Mmm, I love {} too!",
                "{} is such a tasty dish. Great pick!",
                "Oh, {}? That sounds mouthwatering!"
            ],
            "hobbies": [
                "{} sounds like a really fun hobby.",
                "Nice! {} can be so rewarding.",
                "I’ve always wanted to try {}!",
                "You must enjoy {} a lot!"
            ],
            "music": [
                "{}? That’s a great artist!",
                "I enjoy listening to {} too!",
                "{} has such a unique sound.",
                "Listening to {} can really lift your mood!"
            ],
            "movies_and_tv": [
                "{} is a classic!",
                "I’ve seen {} too — it’s really good!",
                "Many people love {}.",
                "Oh, {}? Great choice!"
            ]
        }
       
        # TODO: change these positive feedback responses based on grammar errors
        self.positive_feedback = [
            "That's great!",
            "Interesting!",
            "Thanks for sharing.",
            "I like how you explained that.",
            "You're doing well with your English!"
        ]

        self.topic_transition_templates = [
            "Now let's talk a bit about {}.",
            "Next up: {}!",
            "Let's move on to {}.",
            "How about we shift to {} for a moment?",
            "Time to dive into {}.",
            "Let’s chat about {} now."
        ]
       
        # init
        self.current_topic = random.choice(list(self.practice_topics.keys()))
        self.used_questions = set()
       
        # conversation state
        self.first_interaction = True
        self.asked_name = False
        self.conversation_turns = 0

        self.tokenizer = AutoTokenizer.from_pretrained("grammarly/coedit-large")
        self.model = T5ForConditionalGeneration.from_pretrained("grammarly/coedit-large")
   
    def check_grammar(self, user_text):
        input_text = f'Fix grammatical errors in this sentence: {user_text}.'
        input_ids = self.tokenizer(input_text, return_tensors="pt").input_ids
        outputs = self.model.generate(input_ids, max_length=256)
        edited_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        diffs = self.get_differences(user_text, edited_text)
        feedback = self.explain_differences(diffs, user_text.split(), edited_text.split())
        return feedback, edited_text

    def get_differences(self, original, corrected):
        orig_tokens = original.split()
        corr_tokens = corrected.split()
        matcher = SequenceMatcher(None, orig_tokens, corr_tokens)
        diffs = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                diffs.append({
                    "type": tag,
                    "original": orig_tokens[i1:i2],
                    "corrected": corr_tokens[j1:j2]
                })
        return diffs

    def explain_differences(self, diffs, orig_tokens, corr_tokens):
        feedback = []
        for diff in diffs:
            orig = " ".join(diff["original"])
            corr = " ".join(diff["corrected"])
            if diff["type"] == "replace":
                feedback.append(f"You said '{orig}', but it's more natural to say '{corr}'.")
            elif diff["type"] == "delete":
                feedback.append(f"You said '{orig}', but it can be removed.")
            elif diff["type"] == "insert":
                # find where the insertion happened
                index = corr_tokens.index(diff["corrected"][0])
                before = corr_tokens[index - 1] if index > 0 else ""
                after = corr_tokens[index + len(diff["corrected"])] if index + len(diff["corrected"]) < len(corr_tokens) else ""
                if before and after:
                    feedback.append(f"It’s better to include '{corr}' between '{before}' and '{after}'.")
                elif before:
                    feedback.append(f"It’s better to include '{corr}' after '{before}'.")
                elif after:
                    feedback.append(f"It’s better to include '{corr}' before '{after}'.")
                else:
                    feedback.append(f"It’s better to include '{corr}' somewhere in the sentence.")
        return feedback

    def reset_conversation(self):
        #TODO: create button to do this
        self.user_name = None
        self.user_info = {}
        self.current_topic = random.choice(list(self.practice_topics.keys()))
        self.used_questions = set()
        self.first_interaction = True
        self.asked_name = False
        self.conversation_turns = 0
   
    def get_next_practice_question(self):
        # gets netx practice question and changes topic if no questions available
        prev_topic = self.current_topic
        available_questions = [q for q in self.practice_topics[self.current_topic]
                                if q not in self.used_questions]

        topic_changed = False
        if not available_questions:
            while self.current_topic == prev_topic and len(self.practice_topics) > 1:
                self.current_topic = random.choice(list(self.practice_topics.keys()))
            self.used_questions = set()
            available_questions = self.practice_topics[self.current_topic]
            topic_changed = True

        question = random.choice(available_questions)
        self.used_questions.add(question)
        return question, topic_changed
   
    def detect_user_info(self, user_input):
        # heuristics
        # TODO: make this better
        lower_input = user_input.lower()
        if "my name is" in lower_input and self.user_name is None:
            self.user_name = lower_input.split("my name is", 1)[1].strip().split()[0]
        elif "i am " in lower_input and self.user_name is None:
            self.user_name = lower_input.split("i am", 1)[1].strip().split()[0]
        elif "i'm " in lower_input and self.user_name is None:
            self.user_name = lower_input.split("i'm", 1)[1].strip().split()[0]
   
    def respond(self, user_input):
        # get name using basic rule
        self.detect_user_info(user_input)
        # might delete this
        self.conversation_turns += 1
       
        
        # first interaction
        if self.first_interaction:
            self.first_interaction = False
            if self.user_name:
                question, topic_changed = self.get_next_practice_question() # don't need changed topic
                response = f"Nice to meet you, {self.user_name}! I'm your English practice assistant, jaide. Let's practice with some questions about {self.current_topic.replace('_', ' ')}. {question}"
            else:
                self.asked_name = True
                response = "I couldn't quite catch that. What's your name?"
            return response, None
       
        # I need to rework this as it is awful
        if self.asked_name and self.conversation_turns == 2:
            self.asked_name = False

            if not self.user_name:
                self.user_name = user_input.split()[0]  # I need to make this better
           
            question, topic_changed = self.get_next_practice_question() # don't need changed topic
            response = f"Nice to meet you, {self.user_name}! I'm your English practice assistant, jaide. Let's practice with some questions about {self.current_topic.replace('_', ' ')}. {question}"
            return response, None

        grammar_feedback, edited_sentence = self.check_grammar(user_input)
        doc = nlp(user_input)

        relevant_labels = set()
        if self.current_topic == "travel":
            relevant_labels = {"GPE", "LOC", "FAC"}
        elif self.current_topic == "hobbies":
            relevant_labels = {"PRODUCT", "ORG", "EVENT", "WORK_OF_ART"}

        elif self.current_topic == "food":
            relevant_labels = {"PRODUCT", "ORG"}

        elif self.current_topic == "music":
            relevant_labels = {"PERSON", "ORG", "WORK_OF_ART"}

        elif self.current_topic == "movies_and_tv":
            relevant_labels = {"WORK_OF_ART", "PERSON", "ORG"}

        extracted_entity_text = None
        for ent in doc.ents:
            if ent.label_ in relevant_labels:
                extracted_entity_text = ent.text
                break
        # choose feedback based on entity found or not
        feedback_templates = self.topic_feedback_templates.get(self.current_topic, ["Okay, {}."])
        if extracted_entity_text:
            template = random.choice(feedback_templates)
            feedback = template.format(extracted_entity_text)
        else:
            feedback = random.choice(self.positive_feedback)

        question, topic_changed = self.get_next_practice_question()

        response_data = {
            "feedback": feedback,
            "grammar": grammar_feedback[::] if grammar_feedback else [],
            "question": question
        }

        if topic_changed:
            transition = random.choice(self.topic_transition_templates).format(self.current_topic.replace('_', ' '))
            response_data["transition"] = transition
        print(response_data)
        print(edited_sentence)
        return response_data, edited_sentence

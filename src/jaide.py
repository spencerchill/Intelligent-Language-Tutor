import spacy
import errant
from transformers import AutoTokenizer, T5ForConditionalGeneration
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from res.chat_bot_templates import EXPLANATION_TEMPLATES
import text_processing as tp

from enum import Enum
import random
import re


try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spacy model")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

class ConversationState(Enum):
    INITIAL_GREETING = "INITIAL_GREETING"
    WAITING_FOR_NAME = "WAITING_FOR_NAME"
    CONVERSING = "CONVERSING"

class Jaide:
    def __init__(self):
        self.bot_name = "jaide"
        self.user_name = None       
        ######### IMOPORTANT #########
        # IDGAF RN I'm not extending this just keep it here its good
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
        self.response_templates = {
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
                "I’ve seen {} too, it’s really good!",
                "Many people love {}.",
                "Oh, {}? Great choice!"
            ]
        }

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

        self.topic_entity_labels = {
            "travel": {"GPE", "LOC", "FAC", "ORG"},
            "hobbies": {"PRODUCT", "ORG", "EVENT", "WORK_OF_ART"},
            "food": {"PRODUCT", "ORG", "NORP"},
            "music": {"PERSON", "ORG", "WORK_OF_ART", "EVENT"},
            "movies_and_tv": {"WORK_OF_ART", "PERSON", "ORG", "EVENT"},
        }
       
        # init
        self.current_topic = random.choice(list(self.practice_topics.keys()))
        self.current_question = None
        self.used_questions = set()
        self.conversation_state = ConversationState.INITIAL_GREETING
        
        self.annotator = errant.load('en')
        self.tokenizer = AutoTokenizer.from_pretrained("grammarly/coedit-large")
        self.model = T5ForConditionalGeneration.from_pretrained("grammarly/coedit-large")
        self.annotator = errant.load('en')
   
    def check_grammar(self, user_text):
        input_text = f'Fix grammatical errors in this sentence: {user_text}.'
        input_ids = self.tokenizer(input_text, return_tensors="pt").input_ids
        outputs = self.model.generate(input_ids, max_length=256)
        edited_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        feedback = self.explain_differences(user_text, edited_text)
        return feedback, edited_text

    def detect_name_fallback(self, user_input):
        # fallback if entity extraction fails
        lower_input = user_input.lower()
        
        if len(lower_input.split()) == 1:
            return lower_input.capitalize()
        elif "my name is" in lower_input and self.user_name is None:
            return lower_input.split("my name is", 1)[1].strip().split()[0].capitalize()
        elif "i am " in lower_input and self.user_name is None:
            return lower_input.split("i am", 1)[1].strip().split()[0].capitalize()
        elif "i'm " in lower_input and self.user_name is None:
            return lower_input.split("i'm", 1)[1].strip().split()[0].capitalize()
        else:
            return "Friend"

    def explain_differences(self, original, corrected):
        # remove punctuation, messes IT ALL UPPPP
        cleaned_corrected = re.sub(r'[,.!?]', '', corrected)

        orig_tokens = self.annotator.parse(original)
        cor_tokens  = self.annotator.parse(cleaned_corrected)
        edits = self.annotator.annotate(orig_tokens, cor_tokens)
 
        explanations = []
        for edit in edits:

            original_text = edit.o_str
            corrected_text = edit.c_str
            edit_type = edit.type
            template = EXPLANATION_TEMPLATES.get(edit_type, "The word '{word}' was changed.")

            explanation = template.format(word=original_text, correction=corrected_text)
            explanations.append(explanation)

        return explanations

    def reset_conversation(self):
        self.user_name = None
        self.current_topic = random.choice(list(self.practice_topics.keys()))
        self.used_questions = set()
        self.conversation_state = ConversationState.INITIAL_GREETING
   
    def get_next_practice_question(self):
        # gets next practice question and changes topic if no questions available
        prev_topic = self.current_topic
        available_questions = [q for q in self.practice_topics[self.current_topic]
                                if q not in self.used_questions]

        topic_changed = False
        if not available_questions:
            while self.current_topic == prev_topic:
                self.current_topic = random.choice(list(self.practice_topics.keys()))
            self.used_questions = set()
            available_questions = self.practice_topics[self.current_topic]
            topic_changed = True

        question = random.choice(available_questions)
        self.current_question = question
        self.used_questions.add(question)
        return question, topic_changed

    def get_pronunciation_help(self, word):
        phonemes = tp.text_to_ipa_phoneme(word)
        phoneme_str = " ".join(f"/{phoneme}/" for phoneme in phonemes)
        pronunciation_message = f"Here are the phonemes for '{word}': {phoneme_str}"
        
        question_message = "Now, what's your name?"
        if self.current_question is not None:
            question_message = f"Let's go back to where we were. {self.current_question}"
        return pronunciation_message, question_message

    def respond(self, user_input):
        # === State Checking ===
        if self.conversation_state == ConversationState.INITIAL_GREETING:

            response_text = (
                "Hi there! I'm here to help you learn English. You can either type or speak your responses.\n"
                "        If you'd like pronunciation help, just type 'Help me pronounce [word]'.\n"
                "        For example, you can say 'Help me pronounce apple'.\n"
                "        What's your name?"
            )
            self.conversation_state = ConversationState.WAITING_FOR_NAME
            return response_text, None

        elif self.conversation_state == ConversationState.WAITING_FOR_NAME:
            # try to extract users name
            doc = nlp(user_input)
            name = None
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text.strip().title()
                    break

            self.user_name = name if name else self.detect_name_fallback(user_input)
            greeting = f"Nice to meet you, {self.user_name}! "
            # build response
            self.conversation_state = ConversationState.CONVERSING
            question, topic_changed = self.get_next_practice_question()
            topic_intro = f"Let's practice with some questions about {self.current_topic.replace('_', ' ')}. "
            response = f"{greeting} {topic_intro} {question}"
            return response, None

        elif self.conversation_state == ConversationState.CONVERSING:
            grammar_feedback, edited_sentence = self.check_grammar(user_input)
            relevant_labels = self.topic_entity_labels.get(self.current_topic, set())
            # extract entities relevant to topic
            doc = nlp(edited_sentence)
            extracted_entity_text = None
            for ent in doc.ents:
                if ent.label_ in relevant_labels:
                    extracted_entity_text = ent.text
                    break

            response_comment = ""
            response_template_list = self.response_templates.get(self.current_topic)
            if extracted_entity_text and response_template_list:
                template = random.choice(response_template_list)
                response_comment = template.format(extracted_entity_text)
            else:
                response_comment = random.choice(self.positive_feedback)

            question, topic_changed = self.get_next_practice_question()
            # need to seperate between parts for highlighting
            response_data = {
                "response_comment": response_comment,
                "grammar": grammar_feedback or [],
                "question": question
            }

            if topic_changed:
                transition = random.choice(self.topic_transition_templates).format(self.current_topic.replace('_', ' '))
                response_data["transition"] = transition

            return response_data, edited_sentence
            
if __name__ == "__main__":
    jaide = Jaide()
    orig = "I writed a letter and she don't go to school"
    cor ="I wrote a letter and she doesn't go to school"
    print(jaide.explain_differences(orig, cor))
    
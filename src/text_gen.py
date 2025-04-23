import json
import random
import string
from pathlib import Path

#FILE_PATH = os.path.join( os.path.dirname(os.path.abspath(__file__)), '..', 'res', 'sentences.json')
FILE_PATH = Path(__file__).resolve().parent.parent / 'res' / 'sentences.json'

def gen_random_text(file_path=FILE_PATH):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
                text = json.load(file)

        sentences = [entry["sentence"] for entry in text["data"]]
        random_sentence = random.choice(sentences)
        # remove punctuation
        return random_sentence
        
    except Exception as e:
        print(f"Error: {str(e)}")


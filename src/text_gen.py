import json
import random
from pathlib import Path

#FILE_PATH = os.path.join( os.path.dirname(os.path.abspath(__file__)), '..', 'res', 'sentences.json')
FILE_PATH = Path(__file__).resolve().parent.parent / 'res' / 'sentences.json'

def gen_random_text(file_path=FILE_PATH):
    try:

        with open(file_path, "r") as file:
                text = json.load(file)

        sentences = [entry["sentence"] for entry in text["data"]]
        random_sentence = random.choice(sentences)

        return random_sentence

        
        #Right now just printing but later we can adjust this to show an error box on frontend
        #to do: better error handling
        
  
    except FileNotFoundError as e:
        print(f"{file_path} does not exist")
    except json.JSONDecodeError as e:
        print(f"failed decoding json file at {file_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
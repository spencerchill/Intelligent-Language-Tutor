import torch
import sounddevice as sd
import librosa 

# currently reads audio file. ok for now
def load_audio(audio_path, sample_rate):
    audio_input, sr = librosa.load(audio_path, sr=sample_rate)
    return audio_input

# Speech to text model 
# perhaps looking into. Currently we have our phonemes not segmented (HARD?!)
# I think this would be better
class STTModel:
    def __init__(self, model_name="jonatasgrosman/wav2vec2-large-xlsr-53-english", sample_rate=16000):
        from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

        self.processor = Wav2Vec2Processor.from_pretrained(model_name)
        self.model = Wav2Vec2ForCTC.from_pretrained(model_name)
        self.sample_rate = sample_rate
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() 
            else 'mps' if torch.backends.mps.is_available() 
            else 'cpu'
        )
        self.model.to(self.device)
            
    def transcribe(self, audio_path):
        audio_input = load_audio(audio_path, self.sample_rate)
        input_values = self.processor(audio_input, return_tensors="pt", sampling_rate=self.sample_rate).input_values
        input_values = input_values.to(self.device)

        with torch.no_grad():
            logits = self.model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.processor.decode(predicted_ids[0])

        return transcription


class PhonemeModel:
    def __init__(self, model_name="Bluecast/wav2vec2-Phoneme", sample_rate=16000):
        from transformers import AutoProcessor, AutoModelForCTC
        
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModelForCTC.from_pretrained(model_name)
        self.sample_rate = sample_rate
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() 
            else 'mps' if torch.backends.mps.is_available() 
            else 'cpu'
        )
        self.model.to(self.device)

    def get_phoneme_prediction(self, audio_path):   
        audio_input = load_audio(audio_path, self.sample_rate)
        input_values = self.processor(audio_input, return_tensors="pt", sampling_rate=self.sample_rate).input_values
        input_values = input_values.to(self.device) 

        with torch.no_grad():
            logits = self.model(input_values).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        phonemes = self.processor.decode(predicted_ids[0])

        return phonemes.upper().split()

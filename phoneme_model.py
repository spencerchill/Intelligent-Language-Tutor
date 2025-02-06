import torch
from transformers import AutoProcessor, AutoModelForCTC
import sounddevice as sd
import librosa 

class PhonemeModel:
    def __init__(self, model_name = "Bluecast/wav2vec2-Phoneme", sample_rate = 16000):
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModelForCTC.from_pretrained(model_name)
        self.sample_rate = sample_rate
        self.device = torch.device('cpu')
        # GPU optimization
        
        """
        Uses nvidia GPU if user has CUDA installed
        """

        if torch.cuda.is_available():
            device = torch.device('cuda')
            self.model.to(self.device)
            print(f'Using device: {torch.cuda.get_device_name(0)}')
        else:
            print('Using CPU.')
    
    def load_audio(self, audio_path):
        """
        Currently loading audio file for simplicity. 
        Add record functionality later.
        """
        audio_input, sr = librosa.load(audio_path, sr = self.sample_rate)
        return audio_input
    
    def predict_phonemes(self, audio_input):

        input_values = self.processor(audio_input, return_tensors = "pt").input_values
        input_values = input_values.to(self.device) 

        #make predictions
        with torch.no_grad():
            logits = self.model(input_values).logits

        predicted_ids = torch.argmax(logits, dim = -1)
        phonemes = self.processor.decode(predicted_ids[0])

        return phonemes
    
    def get_phoneme_prediction(self, audio_path):
        """
        This method takes audio path rn.
        """
        audio_input = self.load_audio(audio_path)
        predicted_phonemes = self.predict_phonemes(audio_input)

        return predicted_phonemes

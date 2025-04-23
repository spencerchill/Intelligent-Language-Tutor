import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

import torch
import sounddevice as sd
import librosa 
import threading
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
# currently reads audio file. ok for now
def load_audio(audio_path, sample_rate):
    audio_input, sr = librosa.load(audio_path, sr=sample_rate)
    return audio_input

def play_tts(text):
    """Generate and play TTS of the target phrase."""
    def _play():
        tts_filename = "tts_output.mp3"
        tts = gTTS(text)
        tts.save(tts_filename)

        audio = AudioSegment.from_file(tts_filename, format="mp3")
        play(audio)

    threading.Thread(target=_play, daemon=True).start() # avoid freezing main ui thread

#### DELETE PHONEME MODEL FOR STORAGE ####
# this model might get thrown but i need further testing with whisper
# Whisper model is core to chat bot
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

class WhisperModel:
    def __init__(self, model_name="openai/whisper-small.en", sample_rate=16000):

        from transformers import WhisperProcessor, WhisperForConditionalGeneration
        
        self.processor = WhisperProcessor.from_pretrained(model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name)
        
        self.sample_rate = sample_rate
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() 
            else 'mps' if torch.backends.mps.is_available() 
            else 'cpu'
        )
        self.model.to(self.device)
        self.device = torch.device("cpu")
        self.model.to(self.device)
            
    def transcribe(self, audio_path):
  
        audio_input = load_audio(audio_path, self.sample_rate)
        
        input_features = self.processor(
            audio_input, 
            sampling_rate=self.sample_rate, 
            return_tensors="pt"
        ).input_features
        input_features = input_features.to(self.device)
    
        with torch.no_grad():
            predicted_ids = self.model.generate(input_features)
        
        transcription = self.processor.batch_decode(
            predicted_ids, 
            skip_special_tokens=True
        )[0]
        
        return transcription

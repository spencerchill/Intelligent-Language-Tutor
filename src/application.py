import tkinter as tk
from text_gen import gen_random_text
import text_processing as tp
import error_detection as ed
import models as md
import string  # punctuation removal
import os
import pyaudio
import wave
import threading
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

# Constants for audio recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ILT - Pronunciation Trainer")
        self.root.geometry("800x600")
        self.root.configure(bg="white")

        # Recording state variables
        self.is_recording = False
        self.frames = []
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.audio_filename = None

        # Generate initial text and phoneme
        self.current_text = self.generate_text()
        self.current_phoneme = tp.text_to_ipa_phoneme(self.current_text)

        # UI Components
        self.create_widgets()

    def create_widgets(self):
        """Create and arrange the UI components."""

        # Text Display
        self.text_display = tk.Text(self.root, font=("Arial", 14), wrap="word", width=40, height=4)
        self.text_display.insert("1.0", self.current_text)
        self.text_display.config(state="disabled")
        self.text_display.tag_config("correct", foreground="green")
        self.text_display.tag_config("incorrect", foreground="red")
        self.text_display.pack(padx=20, pady=20)

        # Phoneme Label
        self.phoneme_label = tk.Label(self.root, text=self.current_phoneme, font=("Arial", 12), fg="blue")
        self.phoneme_label.pack(padx=20, pady=10)

        # Buttons
        self.rbtn = tk.Button(self.root, text="Start Recording", bg="white", command=self.toggle_recording)
        self.rbtn.pack(padx=20, pady=10)

        self.play_btn = tk.Button(self.root, text="Play Recording", bg="lightgray", command=self.play_recording, state="disabled")
        self.play_btn.pack(padx=20, pady=10)

        self.tts_btn = tk.Button(self.root, text="Listen to TTS", bg="lightgray", command=self.play_tts)
        self.tts_btn.pack(padx=20, pady=10)

        self.generate_btn = tk.Button(self.root, text="Generate New Text", command=self.generate)
        self.generate_btn.pack(padx=20, pady=20)

    def generate_text(self):
        """Generate a new phrase without punctuation for error detection."""
        return ''.join([char for char in gen_random_text() if char not in string.punctuation])

    def generate(self):
        """Generate new text, update UI, and remove old audio files."""
        # Remove previous recording if exists
        if self.audio_filename and os.path.exists(self.audio_filename):
            os.remove(self.audio_filename)

        # Generate new text and phonemes
        self.current_text = self.generate_text()
        self.current_phoneme = tp.text_to_ipa_phoneme(self.current_text)

        # Update UI
        self.text_display.config(state="normal")
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert("1.0", self.current_text)
        self.text_display.config(state="disabled")
        self.phoneme_label.config(text=self.current_phoneme)

        # Disable play button as there’s no new recording
        self.play_btn.config(state="disabled", bg="lightgray")

    def toggle_recording(self):
        """Toggle the recording state."""
        if not self.is_recording:
            self.is_recording = True
            self.rbtn.config(text="Stop Recording", bg="red")
            threading.Thread(target=self.record_audio, daemon=True).start()
        else:
            self.is_recording = False
            self.rbtn.config(text="Start Recording", bg="white")  # Reset color

    def record_audio(self):
        """Records the user's voice in a separate thread."""
        self.frames = []
        self.stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        print("Recording started...")
        while self.is_recording:
            try:
                data = self.stream.read(CHUNK)
                self.frames.append(data)
            except Exception as e:
                print(f"Error recording audio: {e}")
                break
        print("Recording stopped.")

        # Close stream
        self.stream.stop_stream()
        self.stream.close()

        # Save audio
        self.audio_filename = "user_recording.wav"
        with wave.open(self.audio_filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(self.frames))

        print(f"Audio file saved as {self.audio_filename}")
        self.play_btn.config(state="normal", bg="white")  # Enable playback button

        # Process pronunciation
        threading.Thread(target=self.process_audio, args=(self.audio_filename,), daemon=True).start()

    def process_audio(self, filename):
        """Processes recorded audio and highlights incorrect phonemes."""
        print("Processing audio:", filename)

        # Convert speech to text
        user_text = md.STTModel().transcribe(filename)
        print("Transcription:", user_text)

        # Convert text to phonemes
        user_phonemes = tp.text_to_ipa_phoneme(user_text)
        print("Phonemes:", user_phonemes)

        # Get pronunciation info
        error_info = ed.get_pronunciation_score(self.current_text, tp.text_to_ipa_phoneme(self.current_text), user_phonemes)
        print("Pronunciation info:", error_info)

        self.highlight_text(error_info['incorrect_indices'], len(self.current_text))

    def highlight_text(self, incorrect_indices, total_length):
        """Highlight incorrect letters in the text."""
        self.text_display.config(state="normal")
        self.text_display.tag_remove("incorrect", "1.0", tk.END)
        self.text_display.tag_remove("correct", "1.0", tk.END)
        self.text_display.tag_add("correct", "1.0", f"1.{total_length}")  # Initially mark all green

        for index in incorrect_indices:
            self.text_display.tag_add("incorrect", f"1.{index}", f"1.{index+1}")

        self.text_display.config(state="disabled")

    def play_recording(self):
        """Play the last recorded audio file."""
        if self.audio_filename and os.path.exists(self.audio_filename):
            audio = AudioSegment.from_wav(self.audio_filename)
            play(audio)

    def play_tts(self):
        """Generate and play TTS of the target phrase."""
        tts_filename = "tts_output.mp3"
        tts = gTTS(self.current_text)
        tts.save(tts_filename)
        os.system(tts_filename)  # Play the TTS audio

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = Application()
    app.run()
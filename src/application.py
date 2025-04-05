import tkinter as tk
from text_gen import gen_random_text
import text_processing as tp
import error_detection as ed
import models as md
from audio_recorder import AudioRecorder


class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ILT - Pronunciation Trainer")
        self.root.geometry("800x600")
        self.root.configure(bg="white")
        # my app looks awful on mac as colors are not standardized. feel free to delete when you set a style \
        self.root.option_add("*Background", "white")
        self.root.option_add("*Foreground", "black")
        self.root.option_add("*TButton*Background", "white")
        self.root.option_add("*TButton*Foreground", "white")
        self.root.option_add("*TLabel*Background", "white")
        self.root.option_add("*TLabel*Foreground", "black")
        # Initialize recorder
        self.recorder = AudioRecorder(callback=self.process_audio)
        # Generate initial text and phoneme
        self.current_text = gen_random_text()
        self.current_phoneme = tp.text_to_ipa_phoneme(self.current_text)
        # UI Components
        self.create_widgets()

    def create_widgets(self):
        """Create and arrange the UI components."""
        # current text display
        self.text_display = tk.Text(self.root, font=("Arial", 14), wrap="word", width=40, height=4)
        self.text_display.insert("1.0", self.current_text)
        self.text_display.config(state="disabled")
        self.text_display.tag_config("correct", foreground="green")
        self.text_display.tag_config("incorrect", foreground="red")
        self.text_display.tag_config("partial", foreground="orange")
        self.text_display.pack(padx=20, pady=20)

        # current phoneme display
        self.phoneme_display = tk.Text(self.root, font=("Arial", 12), wrap="word", fg="blue", height=4, width=40)
        self.phoneme_display.insert("1.0", self.current_phoneme)
        self.phoneme_display.config(state="disabled")
        self.phoneme_display.tag_config("correct", foreground="green")
        self.phoneme_display.tag_config("incorrect", foreground="red")
        self.phoneme_display.tag_config("partial", foreground="orange")
        self.phoneme_display.tag_configure("black", foreground="black")
        self.phoneme_display.pack(padx=20, pady=10)

        # buttons
        self.rbtn = tk.Button(self.root, text="Start Recording", bg="white", command=self.toggle_recording)
        self.rbtn.pack(padx=20, pady=10)

        self.play_btn = tk.Button(self.root, text="Play Recording", bg="lightgray", command=self.recorder.play_recording, state="disabled")
        self.play_btn.pack(padx=20, pady=10)

        self.tts_btn = tk.Button(self.root, text="Listen to TTS", bg="lightgray", command=self.play_tts)
        self.tts_btn.pack(padx=20, pady=10)

        self.generate_btn = tk.Button(self.root, text="Generate New Text", command=self.generate)
        self.generate_btn.pack(padx=20, pady=20)

    def generate(self):
        """Generate new text, update UI, and remove old audio files."""
        self.recorder.delete_recording()
        self.current_text = gen_random_text()
        self.current_phoneme = tp.text_to_ipa_phoneme(self.current_text)

        self.text_display.config(state="normal")
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert("1.0", self.current_text)
        self.text_display.config(state="disabled")
        
        self.phoneme_display.config(state="normal")
        self.phoneme_display.delete("1.0", tk.END)
        self.phoneme_display.insert("1.0", self.current_phoneme)
        self.phoneme_display.config(state="disabled")
        # Disable play button as there’s no new recording
        self.play_btn.config(state="disabled", bg="lightgray")

    def toggle_recording(self):
        """Toggle the recording state."""
        if not self.recorder.is_recording():
            self.rbtn.config(text="Stop Recording", bg="red")
            self.recorder.start_recording()
        else:
            self.recorder.stop_recording()
            self.rbtn.config(text="Start Recording", bg="white")  # Reset color
            self.play_btn.config(state="normal", bg="white")

    def process_audio(self, filename):
        """Processes recorded audio and highlights incorrect phonemes."""
        print("Processing audio:", filename)

        user_text = md.STTModel().transcribe(filename)
        print("Transcription:", user_text)
    
        user_phonemes = tp.text_to_ipa_phoneme(user_text)
        print("Phonemes:", user_phonemes)
        
        target_words = self.current_text.split()
        user_words = user_text.split()

        # if user speaks too few or too many words program breaks. we probably wont fix this lol
        if len(target_words) != len(user_words):
            self.highlight_all_red(len(self.current_text))
            return 

        error_info = ed.get_pronunciation_score(self.current_text, self.current_phoneme, user_phonemes)
        # create section for accuracy later 
        self.highlight_text(error_info['incorrect_indices'], len(self.current_text))
        self.highlight_phonemes(error_info['phoneme_indices'], len(self.current_phoneme))

    def highlight_all_red(self, total_length):
        """Highlight phonemes and text red."""
        # should only be called due to issue with error detection
        self.text_display.config(state="normal")
        self.text_display.tag_remove("incorrect", "1.0", tk.END)
        self.text_display.tag_add("incorrect", "1.0", f"1.{total_length}")
        self.text_display.config(state="disabled")

        self.phoneme_display.config(state="normal")
        self.phoneme_display.tag_remove("incorrect", "1.0", tk.END)
        self.phoneme_display.tag_add("incorrect", "1.0", f"1.{total_length}")
        self.phoneme_display.config(state="disabled")
        
    def highlight_phonemes(self, phoneme_indices, total_length):
        """Highlight incorrect phonemes in the phoneme display"""
        self.phoneme_display.config(state="normal")
        self.phoneme_display.tag_remove("incorrect", "1.0", tk.END)
        self.phoneme_display.tag_remove("partial", "1.0", tk.END)
        self.phoneme_display.tag_remove("correct", "1.0", tk.END)
        self.phoneme_display.tag_add("correct", "1.0", f"1.{total_length}")

    # starting position of each word in phoneme string
        phoneme_words = self.current_phoneme.split()
        phoneme_word_starts = []
        pos = 0
        for word in phoneme_words:
            phoneme_word_starts.append(pos)
            pos += len(word) + 1
    
        for word_idx, phoneme_idx, severity in phoneme_indices:
            tag = "incorrect" if severity == "full" else "partial"

            phoneme_pos = phoneme_word_starts[word_idx] + phoneme_idx
            self.phoneme_display.tag_add(tag, f"1.{phoneme_pos}", f"1.{phoneme_pos+1}")

        # slashes at start and end are being considered apart of phonemes for simplicity, always highlight black
        # we can remove the slashes but it signifies to the user those are the IPA phonemes
        self.phoneme_display.tag_add("black", "1.0", "1.1")  # first character
        self.phoneme_display.tag_add("black", f"1.{total_length-1}", f"1.{total_length}") # last character 
        self.phoneme_display.config(state="disabled")

    def highlight_text(self, incorrect_indices, total_length):
        """Highlight incorrect letters in the text"""
        self.text_display.config(state="normal")
        self.text_display.tag_remove("incorrect", "1.0", tk.END)
        self.text_display.tag_remove("partial", "1.0", tk.END)
        self.text_display.tag_remove("correct", "1.0", tk.END)
        self.text_display.tag_add("correct", "1.0", f"1.{total_length}")
        # highlighting target_phrase
        for index, severity in incorrect_indices:
            tag = "incorrect" if severity == "full" else "partial"
            self.text_display.tag_add(tag, f"1.{index}", f"1.{index+1}")
        self.text_display.config(state="disabled")
        
    def play_tts(self):
        md.play_tts(self.current_text)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Application()
    app.run()
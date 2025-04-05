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
        self.display_phoneme = ''.join(self.current_phoneme)
        self.error_info = None
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
        self.text_display.bind("<Button-1>", self.on_word_click)

        # current phoneme display
        self.phoneme_display = tk.Text(self.root, font=("Arial", 14), wrap="word", fg="blue", height=4, width=40)
        self.phoneme_display.insert("1.0", self.display_phoneme)
        self.phoneme_display.config(state="disabled")
        self.phoneme_display.tag_config("correct", foreground="green")
        self.phoneme_display.tag_config("incorrect", foreground="red")
        self.phoneme_display.tag_config("partial", foreground="orange")
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
        self.display_phoneme = ''.join(self.current_phoneme)
        self.error_info = None

        self.text_display.config(state="normal")
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert("1.0", self.current_text)
        self.text_display.config(state="disabled")
        
        self.phoneme_display.config(state="normal")
        self.phoneme_display.delete("1.0", tk.END)
        self.phoneme_display.insert("1.0", self.display_phoneme)
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

        self.error_info = ed.get_pronunciation_score(self.current_text, self.current_phoneme, user_phonemes)
        # create section for accuracy later 
        self.highlight_text(self.error_info['incorrect_indices'], len(self.current_text))
        self.highlight_phonemes(self.error_info['phoneme_indices'], len(self.display_phoneme))

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
        # i thought this would be easy:(
        self.phoneme_display.config(state="normal")
        self.phoneme_display.tag_remove("incorrect", "1.0", tk.END)
        self.phoneme_display.tag_remove("partial", "1.0", tk.END)
        self.phoneme_display.tag_remove("correct", "1.0", tk.END)
        self.phoneme_display.tag_add("correct", "1.0", f"1.{total_length}")

        phoneme_words = ed.split_phonemes(self.current_phoneme) 
        # character position for each phoneme
        char_positions = []
        current_pos = 0
        
        for word in phoneme_words:
            word_positions = []
            for phoneme in word:
                word_positions.append(current_pos)
                # count the actual characters in the phoneme
                current_pos += len(phoneme)
            char_positions.append(word_positions)
            current_pos += 1  # space between words
        # highlighting
        for word_idx, phoneme_idx, severity in phoneme_indices:
            if word_idx < len(char_positions) and phoneme_idx < len(char_positions[word_idx]):
                tag = "incorrect" if severity == "full" else "partial"
                start_pos = char_positions[word_idx][phoneme_idx]
                phoneme_length = len(phoneme_words[word_idx][phoneme_idx])
                self.phoneme_display.tag_add(tag, f"1.{start_pos}", f"1.{start_pos + phoneme_length}")
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
    
    def on_word_click(self, event):
        index = self.text_display.index(f"@{event.x},{event.y}")
        word_start = self.text_display.index(f"{index} wordstart")
        word_end = self.text_display.index(f"{index} wordend")
        clicked_word = self.text_display.get(word_start, word_end).strip()
        
        if clicked_word:
            print(word_start)
            print(word_end)
            print(self.get_clicked_word(word_start, word_end, clicked_word))
    
    def get_clicked_word(self, word_start, word_end, clicked_word):
        if self.error_info == None:
            # user hasnt processed audio yet diff logic tbd
            return clicked_word

        start_index = int(word_start.split('.')[1])
        end_index = int(word_end.split('.')[1])
        # iterate through the words in word_feedback and check for the clicked position
        for word in self.error_info['word_feedback']:
            if word['start_index'] <= start_index <= word['end_index'] and word['start_index'] <= end_index <= word['end_index']:
                return word['word'], word['errors']

    def play_tts(self):
        md.play_tts(self.current_text)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Application()
    app.run()
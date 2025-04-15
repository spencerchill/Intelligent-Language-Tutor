import tkinter as tk
from text_gen import gen_random_text
import text_processing as tp
import error_detection as ed
import models as md
from audio_recorder import AudioRecorder
from pronunciation_panel import PronunciationPanel

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

        self.model = md.STTModel()
        self.error_info = None
        self.panel = PronunciationPanel(self.root, tts_callback=self.play_tts)
        # UI Components
        self.create_widgets()

    def create_widgets(self):
        """Create and arrange the UI components."""
        # current text display
        self.text_display = tk.Text(self.root, font=("Inter", 14), wrap="word", width=40, height=4)
        self.text_display.insert("1.0", self.current_text)
        self.text_display.config(state="disabled")
        self.text_display.tag_config("correct", foreground="green")
        self.text_display.tag_config("incorrect", foreground="red")
        self.text_display.tag_config("partial", foreground="orange")
        self.text_display.pack(padx=20, pady=20)
        self.text_display.bind("<Button-1>", self.on_word_click)

        # current phoneme display
        self.phoneme_display = tk.Text(self.root, font=("Inter", 14), wrap="word", fg="blue", height=4, width=40)
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

        self.tts_btn = tk.Button(self.root, text="Listen to TTS", bg="lightgray", command=lambda: self.play_tts(self.current_text))
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

        user_text = self.model.transcribe(filename)
        # audio processing finished
        print("User Transcription:", user_text)
    
        user_phonemes = tp.text_to_ipa_phoneme(user_text)
        print("User Phonemes:", user_phonemes)
        
        target_words = self.current_text.split()
        user_words = user_text.split()

        # basically user didnt even try. just highlight all wrong
        if abs(len(user_words) - len(target_words)) > 4:
            return self.highlight_all_red()

        self.error_info = ed.get_pronunciation_score(self.current_text, self.current_phoneme, user_phonemes)
        # TODO: please create section for accuracy later i have the error_info done for it just grab it
        self.highlight_text(self.error_info['incorrect_indices'])
        self.highlight_phonemes(self.error_info['phoneme_indices'])
        
    def highlight_all_red(self):
        # should only be called if user doesnt even try. 
        self.text_display.config(state="normal")
        self.text_display.tag_remove("incorrect", "1.0", tk.END)
        self.text_display.tag_add("incorrect", "1.0", tk.END)
        self.text_display.config(state="disabled")

        self.phoneme_display.config(state="normal")
        self.phoneme_display.tag_remove("incorrect", "1.0", tk.END)
        self.phoneme_display.tag_add("incorrect", "1.0", tk.END)
        self.phoneme_display.config(state="disabled")
        # you can add more visual feedback if you want afterwards

    def highlight_phonemes(self, phoneme_indices):
        self.phoneme_display.config(state="normal")
        self.phoneme_display.tag_remove("incorrect", "1.0", tk.END)
        self.phoneme_display.tag_remove("partial", "1.0", tk.END)
        self.phoneme_display.tag_remove("correct", "1.0", tk.END)
        self.phoneme_display.tag_add("correct", "1.0", tk.END)

        for phoneme_idx, severity in phoneme_indices:
            # need to know starting pos by adding num characters for each index upto current
            # this is because phonemes are displayed as flat list and processed split
            start_pos = sum(len(self.current_phoneme[i]) for i in range(phoneme_idx))
            phoneme_length = len(self.current_phoneme[phoneme_idx])
            self.phoneme_display.tag_add(severity, f"1.{start_pos}", f"1.{start_pos + phoneme_length}")

        self.phoneme_display.config(state="disabled")

    def highlight_text(self, incorrect_indices):
        """Highlight incorrect letters in the text_display"""
        self.text_display.config(state="normal")
        self.text_display.tag_remove("incorrect", "1.0", tk.END)
        self.text_display.tag_remove("partial", "1.0", tk.END)
        self.text_display.tag_remove("correct", "1.0", tk.END)
        self.text_display.tag_add("correct", "1.0", tk.END)
        # highlighting target_phrase
        for index, severity in incorrect_indices:
            self.text_display.tag_add(severity, f"1.{index}", f"1.{index+1}")
        self.text_display.config(state="disabled")
    
    def on_word_click(self, event):
        # hide panel if already showing
        if self.panel.is_visible:
            self.panel.hide()
            return
        index = self.text_display.index(f"@{event.x},{event.y}")
        word_start = self.text_display.index(f"{index} wordstart")
        word_end = self.text_display.index(f"{index} wordend")
        clicked_word = self.text_display.get(word_start, word_end).strip()

        if clicked_word:
            if self.error_info is None:
                # user hasnt processed audio yet, just play the word
                self.play_tts(clicked_word)
                return
            word_info = self.get_clicked_word_info(word_start, word_end, clicked_word)
            #                          index for phoneme word
            word, phonemes = word_info
            # x y coord of cursor 
            x = self.root.winfo_pointerx() - self.root.winfo_rootx()
            y = self.root.winfo_pointery() - self.root.winfo_rooty()
            self.panel.show(x, y, word, phonemes)

    def get_clicked_word_info(self, word_start, word_end, clicked_word):
        start_index = int(word_start.split('.')[1])
        end_index = int(word_end.split('.')[1])
        # get the word info for the word clicked
        for word_feedback in self.error_info['word_feedback']:
            if start_index <= word_feedback['char_start_index'] and \
                end_index <= word_feedback['char_end_index']:
                return word_feedback['word'], word_feedback['phonemes']
        # if it reaches this i have failed you
        return None

    def play_tts(self, text):
        md.play_tts(text)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
   app = Application()
   app.run()
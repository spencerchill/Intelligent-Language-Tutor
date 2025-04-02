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
        self.current_phoneme = tp.text_to_phoneme(self.current_text)
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
        self.text_display.pack(padx=20, pady=20)
        # current phoneme label
        self.phoneme_label = tk.Label(self.root, text=self.current_phoneme, font=("Arial", 12), fg="blue")
        self.phoneme_label.pack(padx=20, pady=10)

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
        self.current_text = gen_random_text()
        self.current_phoneme = tp.text_to_phoneme(self.current_text)

        self.text_display.config(state="normal")
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert("1.0", self.current_text)
        self.text_display.config(state="disabled")
        self.phoneme_label.config(text=self.current_phoneme)

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

        user_phonemes = tp.text_to_phoneme(user_text)

        error_info = ed.get_pronunciation_score(self.current_text, self.current_phoneme, user_phonemes)

        self.highlight_text(error_info['incorrect_indices'], len(self.current_text))

    def highlight_text(self, incorrect_indices, total_length):
        """Highlight incorrect letters in the text."""
        self.text_display.config(state="normal")
        self.text_display.tag_remove("incorrect", "1.0", tk.END)
        self.text_display.tag_remove("correct", "1.0", tk.END)

        self.text_display.tag_add("correct", "1.0", f"1.{total_length}")

        for index in incorrect_indices:
            self.text_display.tag_add("incorrect", f"1.{index}", f"1.{index+1}")
        self.text_display.config(state="disabled")

    def play_tts(self):
        """Generate and play TTS of the target phrase."""
        md.play_tts(self.current_text)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Application()
    app.run()

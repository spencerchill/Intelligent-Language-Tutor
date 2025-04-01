import tkinter as tk
from text_gen import gen_random_text
import text_processing as tp
import error_detection as ed
import models as md
from audio_recorder import AudioRecorder
import string  # punctuation removal
import threading


# TODO: clean code structure up and make app look pretty like my mom :)
# TODO: remove audio file after user goes to new phrase
# TODO: record button is green after user stops recording. Reset it to white.
# TODO: highlight incorrect phonemes in phoneme label (i might do this one)
# TODO: add the ability to listen to your own recording
# TODO: add the ability to listen to TTS of target_phrase
# IMPORTANT: I stripped the target phrase of punctuations for error detection.
#             we can add this back when we find a way to handle it
#             probably involves kepping track of punctuation indices.


class Application:
    def __init__(self):
        self.current_text = gen_random_text().translate(str.maketrans("", "", ".,")) 
        # The idea is to have multiple scenes. Where application handles switching
        # for now we don't but if you make method need variable make it instanced like text_display
        self.text_display = None
        self.current_phoneme = tp.text_to_phoneme(self.current_text)
        self.recorder = AudioRecorder(callback=self.process_audio)

    def process_audio(self, filename):
        """Analyze pronunciation from audio."""
        print("Processing audio:", filename)
        # convert speech to text
        user_text = md.STTModel().transcribe(filename)
        print("Transcription: ", user_text)
        # convert text to phonemes
        user_phonemes = tp.text_to_phoneme(user_text)
        print("Phonemes: ", user_phonemes)
        # get pronunciation info, such as accuracy and incorrect indices
        error_info = ed.get_pronunciation_score(
            self.current_text, self.current_phoneme, user_phonemes
        )
        print("Pronunciation info:", error_info)

        self.highlight_text(error_info["incorrect_indices"], len(self.current_text))

    def highlight_text(self, incorrect_indices, total_length):
        """Highlight incorrect letters in the text"""
        self.text_display.config(state="normal")
        self.text_display.tag_remove("incorrect", "1.0", tk.END)  # previous highlights
        self.text_display.tag_remove("correct", "1.0", tk.END)

        self.text_display.tag_add(
            "correct", "1.0", f"1.{total_length}"
        )  # entire text is green first

        for index in incorrect_indices:
            self.text_display.tag_add("incorrect", f"1.{index}", f"1.{index+1}")
            self.text_display.config(state="disabled")

    def app(self):
        def toggle_recording():
            """Toggle the recording state when the button is pressed"""
            if not self.recorder.is_recording():
                rbtn.config(text="Stop Recording", bg="red")
                self.recorder.start_recording()
            else:
                self.recorder.stop_recording()
                rbtn.config(text="Start Recording", bg="green")

        # GUI
        root = tk.Tk()
        root.configure(bg="white")
        root.title("ILT")
        root.geometry("800x600")
        # my app looks awful on mac as colors are not standardized. feel free to delete when you set a style \
        root.option_add("*Background", "white")
        root.option_add("*Foreground", "black")
        root.option_add("*TButton*Background", "white")
        root.option_add("*TButton*Foreground", "white")
        root.option_add("*TLabel*Background", "white")
        root.option_add("*TLabel*Foreground", "black")


        # Labels for Text and Phonemes
        # changed textlabel to textdisplay for highlighting
        # also keep style consistent pls
        self.text_display = tk.Text(
            root, font=("Arial", 14), wrap="word", width=40, height=4
        )  # change options how you see fit
        self.text_display.insert("1.0", self.current_text)
        self.text_display.config(state="disabled")
        self.text_display.tag_config("correct", foreground="green")
        self.text_display.tag_config("incorrect", foreground="red")

        phoneme_label = tk.Label(
            root, text=self.current_phoneme, font=("Arial", 12), fg="blue"
        )
        # =currentPhoneme, font=("Arial", 12), fg="blue")

        def generate():
            """Generates new text and updates both labels."""
            # removing punctuation for error detection (working on it)
            self.current_text = gen_random_text().translate(str.maketrans("", "", ".,"))
            self.current_phoneme = tp.text_to_phoneme(self.current_text)

            self.text_display.config(state="normal")
            self.text_display.delete("1.0", tk.END)
            self.text_display.insert("1.0", self.current_text)
            self.text_display.config(state="disabled")

            phoneme_label.config(text=self.current_phoneme)

        # Buttons
        rbtn = tk.Button(root, text="Start Recording", command=toggle_recording)
        generate_btn = tk.Button(root, text="Generate New Text", command=generate)

        # Layout
        self.text_display.pack(padx=20, pady=20)
        phoneme_label.pack(padx=20, pady=10, side="top")
        generate_btn.pack(padx=20, pady=20, side="bottom")
        rbtn.pack(padx=20, pady=20, side="bottom")

        root.mainloop()


if __name__ == "__main__":
    app = Application()
    app.app()

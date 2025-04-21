import tkinter as tk
from text_gen import gen_random_text
import text_processing as tp
import error_detection as ed
import models as md
from audio_recorder import AudioRecorder
import matplotlib.pyplot as plt
from scipy.io import wavfile
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Application:
    def __init__(self):

        # Style Elements
        self.background = "#111111"
        self.box_color = "#222222"
        self.title_font = "Lora 20 bold"
        self.font = "Lora 16"
        self.text_fill = "#ffffff"

        # Tab Booleans
        self.speech_enable = True
        self.spectrogram_enable = False
        self.ai_model_enable = False

        # Defining Root
        self.root = tk.Tk()
        self.root.configure(bg=self.background)
        self.root.title("Language Tutor")
        self.root.geometry("800x600")

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

        #Title Canvas

        self.title_canvas = tk.Canvas(self.root, width=700, height=60, 
                                      borderwidth=0, highlightthickness=0, bg=self.background)
        self.title_canvas.pack(pady=30)

        def round_rectangle(x1, y1, x2, y2, radius=25, **kwargs):
            
            points = [x1+radius, y1,
                        x1+radius, y1,
                        x2-radius, y1,
                        x2-radius, y1,
                        x2, y1,
                        x2, y1+radius,
                        x2, y1+radius,
                        x2, y2-radius,
                        x2, y2-radius,
                        x2, y2,
                        x2-radius, y2,
                        x2-radius, y2,
                        x1+radius, y2,
                        x1+radius, y2,
                        x1, y2,
                        x1, y2-radius,
                        x1, y2-radius,
                        x1, y1+radius,
                        x1, y1+radius,
                        x1, y1]

            return self.title_canvas.create_polygon(points, **kwargs, smooth=True)

        my_rectangle = round_rectangle(0, 0, 700, 60, radius=40, fill=self.box_color)

        self.title_canvas.create_text(350, 30, text="Language Tutor", font=self.title_font, 
                                      fill=self.text_fill)

        #Tab Bar Canvas

        self.tab_bar_canvas = tk.Canvas(self.root, width=600, height=60, borderwidth=0, highlightthickness=0, bg=self.background)
        self.tab_bar_canvas.pack(pady=0)

        self.speech_btn = tk.Button(text="Speech", font=self.font, fg=self.text_fill,
                                    borderwidth=0, highlightthickness=0, bg=self.background,
                                    command=self.speech_click)
        self.spectrogram_btn = tk.Button(text="Spectrogram", font=self.font, fg=self.text_fill,
                                         borderwidth=0, highlightthickness=0, bg=self.background,
                                         command=self.spectrogram_click)
        self.ai_model_btn = tk.Button(text="AI Model", font=self.font, fg=self.text_fill,
                                      borderwidth=0, highlightthickness=0, bg=self.background,
                                      command=self.ai_model_click)

        self.tab_bar_canvas.create_window(150, 30, window=self.speech_btn)
        self.tab_bar_canvas.create_window(300, 30, window=self.spectrogram_btn)
        self.tab_bar_canvas.create_window(450, 30, window=self.ai_model_btn)

        self.tab_selected_bar = tk.PhotoImage(file="images/tab_bar.png")
        self.tab_image_id = self.tab_bar_canvas.create_image(150, 50, image=self.tab_selected_bar)

        #Gen Text Canvas

        self.gen_text_canvas = tk.Canvas(self.root, width=600, height=100, borderwidth=0, 
                                         highlightthickness=0, bg=self.background)
        self.gen_text_canvas.pack(pady=0)

            #Text Display
        self.text_display = tk.Text(self.gen_text_canvas, font=self.font, 
                                    wrap="word", width=40, height=4,
                                    borderwidth=0, highlightthickness=0,
                                    background=self.box_color,
                                    fg=self.text_fill)
        self.text_display.insert("1.0", self.current_text)
        self.text_display.config(state="disabled")
        self.text_display.tag_config("correct", foreground="green")
        self.text_display.tag_config("incorrect", foreground="red")
        self.text_display.tag_config("partial", foreground="orange")
        self.text_display.bind("<Button-1>", self.on_word_click)

        def round_rectangle(x1, y1, x2, y2, radius=25, **kwargs):
            
            points = [x1+radius, y1,
                        x1+radius, y1,
                        x2-radius, y1,
                        x2-radius, y1,
                        x2, y1,
                        x2, y1+radius,
                        x2, y1+radius,
                        x2, y2-radius,
                        x2, y2-radius,
                        x2, y2,
                        x2-radius, y2,
                        x2-radius, y2,
                        x1+radius, y2,
                        x1+radius, y2,
                        x1, y2,
                        x1, y2-radius,
                        x1, y2-radius,
                        x1, y1+radius,
                        x1, y1+radius,
                        x1, y1]

            return self.gen_text_canvas.create_polygon(points, **kwargs, smooth=True)

        my_rectangle = round_rectangle(0, 0, 600, 100, radius=40, fill=self.box_color)

        self.gen_text_canvas.create_window(300, 50, window=self.text_display)

        self.gen_play_image = tk.PhotoImage(file="images/play.png")

        self.gen_play_button = tk.Button(self.root, image=self.gen_play_image, 
                                      borderwidth=0, background=self.box_color, 
                                      activebackground=self.box_color,
                                      command=self.play_tts)
        
        self.gen_text_canvas.create_window(550, 50, window=self.gen_play_button)

        #User Phoneme Canvas

        self.user_phoneme_canvas = tk.Canvas(self.root, width=600, height=100, borderwidth=0, 
                                             highlightthickness=0, bg=self.background)
        self.user_phoneme_canvas.pack(pady=20)

            #User Phoneme Display
        self.phoneme_display = tk.Text(self.user_phoneme_canvas, font=self.font, wrap="word", 
                                       fg="blue", height=4, width=40,
                                       borderwidth=0, highlightthickness=0,
                                       background=self.box_color)
        self.phoneme_display.insert("1.0", self.display_phoneme)
        self.phoneme_display.config(state="disabled")
        self.phoneme_display.tag_config("correct", foreground="green")
        self.phoneme_display.tag_config("incorrect", foreground="red")
        self.phoneme_display.tag_config("partial", foreground="orange")

        def round_rectangle(x1, y1, x2, y2, radius=25, **kwargs):
            
            points = [x1+radius, y1,
                        x1+radius, y1,
                        x2-radius, y1,
                        x2-radius, y1,
                        x2, y1,
                        x2, y1+radius,
                        x2, y1+radius,
                        x2, y2-radius,
                        x2, y2-radius,
                        x2, y2,
                        x2-radius, y2,
                        x2-radius, y2,
                        x1+radius, y2,
                        x1+radius, y2,
                        x1, y2,
                        x1, y2-radius,
                        x1, y2-radius,
                        x1, y1+radius,
                        x1, y1+radius,
                        x1, y1]

            return self.user_phoneme_canvas.create_polygon(points, **kwargs, smooth=True)

        my_rectangle = round_rectangle(0, 0, 600, 100, radius=40, fill=self.box_color)

        self.user_phoneme_canvas.create_window(300, 50, window=self.phoneme_display)

        self.user_play_image = tk.PhotoImage(file="images/play.png")

        self.user_play_button = tk.Button(self.root, image=self.user_play_image, 
                                      borderwidth=0, background=self.box_color, 
                                      activebackground=self.box_color,
                                      command=self.recorder.play_recording, state="disabled")
        
        self.user_phoneme_canvas.create_window(550, 50, 
                                               window=self.user_play_button)

        #Record Button Canvas

        self.rbtn_canvas = tk.Canvas(self.root, width=50, height=50, borderwidth=0, 
                                     highlightthickness=0, bg=self.background)
        self.rbtn_canvas.pack(pady=0)

        self.rbtn_green_image = tk.PhotoImage(file="images/rbtn_green.png")

        self.rbtn_red_image = tk.PhotoImage(file="images/rbtn_red.png")

        self.rbtn = tk.Button(self.rbtn_canvas, image=self.rbtn_green_image,
                                      borderwidth=0, background=self.background, 
                                      activebackground=self.background,
                                      command=self.toggle_recording)
        self.rbtn_canvas.create_window(25, 25, window=self.rbtn)


        #Check Button Canvas

        self.check_canvas = tk.Canvas(self.root, width=50, height=50, borderwidth=0, 
                                      highlightthickness=0, bg=self.background)
        self.check_canvas.pack(pady=20)

        self.check_image = tk.PhotoImage(file="images/check.png")

        self.check_button = tk.Button(self.check_canvas, image=self.check_image,
                                      borderwidth=0, background=self.background,
                                      activebackground=self.background,
                                      command=self.generate)
        self.check_canvas.create_window(25, 25, window=self.check_button)

        # Spectrogram Canvas
        self.spectrogram_canvas = tk.Canvas(self.root, width=100, height=100, borderwidth=0, 
                                      highlightthickness=0, bg=self.background)
        
        self.spectrogram_canvas.create_text(50, 50, text="Spectrogram")

        #AI Model Canvas
        self.ai_model_canvas = tk.Canvas(self.root, width=100, height=100, borderwidth=0, 
                                      highlightthickness=0, bg=self.background)
        
        self.ai_model_canvas.create_text(50, 50, text="AI Model")

    def show_spectrogram(self):
        filename = "user_recording.wav"
        if not filename:
            print("No recording available.")
            return

        try:
            # Read audio
            rate, data = wavfile.read(filename)

            # Clear previous plot if needed
            for widget in self.spectrogram_canvas.winfo_children():
                widget.destroy()

            # Plot spectrogram
            fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
            ax.specgram(data, Fs=rate, NFFT=1024, noverlap=512, cmap="inferno")
            ax.set_title("Spectrogram")
            ax.set_xlabel("Time")
            ax.set_ylabel("Frequency")
            fig.tight_layout()

            # Embed matplotlib figure into Tkinter canvas
            canvas = FigureCanvasTkAgg(fig, master=self.spectrogram_canvas)
            canvas.draw()
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack()

        except Exception as e:
            print("Error generating spectrogram:", e)

    # Tab Bar Methods
    def speech_click(self):
        if not self.speech_enable:

            if self.spectrogram_enable:
                self.tab_bar_canvas.move(self.tab_image_id, -150, 0)
                self.disable_spectrogram_ui()
            
            if self.ai_model_enable:
                self.tab_bar_canvas.move(self.tab_image_id, -300, 0)
                self.disable_ai_model_ui()
            
            self.enable_speech_ui()
            self.root.update()

    def spectrogram_click(self):
        if not self.spectrogram_enable:

            if self.speech_enable:
                self.tab_bar_canvas.move(self.tab_image_id, 150, 0)
                self.disable_speech_ui()

            if self.ai_model_enable:
                self.tab_bar_canvas.move(self.tab_image_id, -150, 0)
                self.disable_ai_model_ui()
            
            self.enable_spectrogram_ui()
            self.root.update()

    def ai_model_click(self):
        if not self.ai_model_enable:
            
            if self.speech_enable:
                self.tab_bar_canvas.move(self.tab_image_id, 300, 0)
                self.disable_speech_ui()

            if self.spectrogram_enable:
                self.tab_bar_canvas.move(self.tab_image_id, 150, 0)
                self.disable_spectrogram_ui()
            
            self.enable_ai_model_ui()
            self.root.update()

    def enable_speech_ui(self):
        self.speech_enable = True
        self.gen_text_canvas.pack()
        self.user_phoneme_canvas.pack(pady=20)
        self.rbtn_canvas.pack()
        self.check_canvas.pack(pady=20)
        self.root.update()

    def disable_speech_ui(self):
        self.speech_enable = False
        self.gen_text_canvas.pack_forget()
        self.user_phoneme_canvas.pack_forget()
        self.rbtn_canvas.pack_forget()
        self.check_canvas.pack_forget()
        self.root.update()

    def enable_spectrogram_ui(self):
        self.spectrogram_enable = True
        self.spectrogram_canvas.pack()
        self.show_spectrogram()
        self.root.update()

    def disable_spectrogram_ui(self):
        self.spectrogram_enable = False
        self.spectrogram_canvas.pack_forget()
        self.root.update()
    
    def enable_ai_model_ui(self):
        self.ai_model_enable = True
        self.ai_model_canvas.pack()
        self.root.update()
    
    def disable_ai_model_ui(self):
        self.ai_model_enable = False
        self.ai_model_canvas.pack_forget()
        self.root.update()


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
        self.user_play_button.config(state="disabled", bg="lightgray")

    def toggle_recording(self):
        """Toggle the recording state."""
        if not self.recorder.is_recording():
            self.rbtn.config(image=self.rbtn_red_image)
            self.recorder.start_recording()
        else:
            self.recorder.stop_recording()
            self.rbtn.config(image=self.rbtn_green_image)  # Reset color
            self.user_play_button.config(state="normal", bg="white")

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
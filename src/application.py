import tkinter as tk
from text_gen import gen_random_text
import text_processing as tp
import error_detection as ed
import models as md
from audio_recorder import AudioRecorder

import matplotlib.pyplot as plt
from scipy.io import wavfile
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


from pronunciation_panel import PronunciationPanel


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

        self.model = md.STTModel()
        self.error_info = None
        self.panel = PronunciationPanel(self.root, tts_callback=self.play_tts)
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

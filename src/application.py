import tkinter as tk
from tkinter import ttk
from text_gen import gen_random_text
import text_processing as tp
import error_detection as ed
import models as md
from audio_recorder import AudioRecorder
import matplotlib.pyplot as plt
from scipy.io import wavfile
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


from pronunciation_panel import PronunciationPanel
from jaide_gui import JaideGUI

class Application:
    def __init__(self):
        # Style Elements WHITE VERSION.
        # NOTE: If you add a toggle for themes you need
        #       to pass the flag to the jaide_gui to then change its theme
        self.background = "#e9ecef"
        self.box_color = "white"
        self.title_font = "Nunito 30 bold"
        self.font = "Inter 12"
        self.text_fill = "black"

        self.speech_enable = True
        self.spectrogram_enable = False
        self.ai_model_enable = False


        self.root = tk.Tk()
        self.root.title("Language Tutor")
        self.root.geometry("800x600") 
        self.root.resizable(0,0)

        #### DO NOT DELETE TS MAC DEFAULTS TO BLACK ALWAYS ####
        self.root.configure(bg=self.background)
        self.root.option_add("*Background", self.background)
        self.root.option_add("*Foreground", "black")
        self.root.option_add("*TButton*Background", self.background)
        self.root.option_add("*TButton*Foreground", self.background)
        self.root.option_add("*TLabel*Background", self.background)
        self.root.option_add("*TLabel*Foreground", "black")
        ####_______________________________________________####
        self.recorder = AudioRecorder(callback=self.process_audio, tag="pronunciation")
        self.stt_model = md.STTModel()

        self.current_text = gen_random_text()
        self.current_phoneme = tp.text_to_ipa_phoneme(self.current_text)
        self.display_phoneme = ''.join(self.current_phoneme)
        self.error_info = None

        self.panel = PronunciationPanel(self.root, tts_callback=self.play_tts)

        self.jaide_gui = JaideGUI(self.root, self.recorder)
        self.jaide_gui_frame = self.jaide_gui.container

        # UI Components
        self.create_widgets()

        self.disable_ai_model_ui() 
        self.enable_speech_ui()

    def create_widgets(self):
        style = ttk.Style()
        ##### TAB BUTTON STYLE #####
        style.configure("Custom.TButton",
                        font="Inter 12",
                        foreground=self.text_fill,
                        background="white",
                        relief="flat")

        style.map("Custom.TButton",
                background=[("active", "#78c2ad")], # mint color
                foreground=[("active", "white")])
        
        self.screen_width=(int) (self.root.winfo_width())
        self.screen_height= (int) (self.root.winfo_height())

        ##### TITLE #####
        self.title_canvas = tk.Canvas(self.root, width=700, height=60,
                                       borderwidth=0, highlightthickness=0, bg=self.background)
        self.title_canvas.pack(pady=30)

        def round_rectangle_title(x1, y1, x2, y2, radius=25, **kwargs):
            points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
            return self.title_canvas.create_polygon(points, **kwargs, smooth=True)
        my_rectangle_title = round_rectangle_title(0, 0, 700, 60, radius=40, fill=self.box_color)
        self.title_canvas.create_text(351, 30, text="Language Tutor", font=self.title_font, fill="gray")
        self.title_canvas.create_text(350, 30, text="Language Tutor", font=self.title_font, fill="#78c2ad")

        separator = ttk.Separator(self.root, orient="horizontal")
        separator.pack(fill="x")


        ##### TAB BAR AND BUTTONS ####
        self.tab_bar_canvas = tk.Canvas(self.root, width=600, height=60, borderwidth=0, highlightthickness=0, bg=self.background)
        self.tab_bar_canvas.pack(pady=0)

        self.speech_btn = ttk.Button(
            text="Speech",
            command=self.speech_click,
            style="Custom.TButton"
        )

        self.spectrogram_btn = ttk.Button(
            text="Spectrogram",
            command=self.spectrogram_click,
            style="Custom.TButton"
        )

        self.ai_model_btn = ttk.Button(
            text="AI Tutor",
            command=self.ai_model_click,
            style="Custom.TButton"
        )

        self.tab_bar_canvas.create_window(150, 30, window=self.speech_btn)
        self.tab_bar_canvas.create_window(300, 30, window=self.spectrogram_btn)
        self.tab_bar_canvas.create_window(450, 30, window=self.ai_model_btn)

        self.tab_selected_bar = tk.PhotoImage(file="images/tab_bar.png")
        self.tab_image_id = self.tab_bar_canvas.create_image(150, 50, image=self.tab_selected_bar)

        ##### TEXT CANVAS #####
        self.gen_text_canvas = tk.Canvas(self.root, width=600, height=100, borderwidth=0,
                                         highlightthickness=0, bg=self.background)
                              
        self.text_display = tk.Text(self.gen_text_canvas, font=self.font,
                                    wrap="word", width=40, height=4,
                                    borderwidth=0, highlightthickness=0,
                                    background=self.box_color,
                                    fg=self.text_fill,
                                    padx=(8))
                                    
        self.text_display.insert("1.0", self.current_text)
        self.text_display.config(state="disabled")
        self.text_display.tag_config("correct", foreground="green")
        self.text_display.tag_config("incorrect", foreground="red")
        self.text_display.tag_config("partial", foreground="orange")
        self.text_display.bind("<Button-1>", self.on_word_click)

        def round_rectangle_gen(x1, y1, x2, y2, radius=25, **kwargs):
             points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
             return self.gen_text_canvas.create_polygon(points, **kwargs, smooth=True)
        my_rectangle_gen = round_rectangle_gen(0, 0, 600, 100, radius=40, fill=self.box_color)
        self.gen_text_canvas.create_window(300, 70, window=self.text_display)

        self.gen_play_button = ttk.Button (
            text="🎧Listen",
            command=lambda: self.play_tts(self.current_text),
            style="Custom.TButton",
            width=7
        )

        self.gen_text_canvas.create_window(550, 50, window=self.gen_play_button)

        self.target_phrase_label = tk.Label(text="Target Phrase", font="Inter 12 bold", fg="#78c2ad", bg=self.box_color)
        self.gen_text_canvas.create_window(300, 15, window=self.target_phrase_label)

        #### PHONEMES ####
        self.user_phoneme_canvas = tk.Canvas(self.root, width=600, height=100, borderwidth=0,
                                             highlightthickness=0, bg=self.background)

        self.phoneme_display = tk.Text(self.user_phoneme_canvas, font=self.font, wrap="word",
                                       fg=self.text_fill, height=4, width=40,
                                       borderwidth=0, highlightthickness=0,
                                       background=self.box_color,
                                       padx=(8))
                                    
        self.phoneme_display.insert("1.0", self.display_phoneme)
        self.phoneme_display.config(state="disabled")
        self.phoneme_display.tag_config("correct", foreground="green")
        self.phoneme_display.tag_config("incorrect", foreground="red")
        self.phoneme_display.tag_config("partial", foreground="orange")

        def round_rectangle_user(x1, y1, x2, y2, radius=25, **kwargs):
             points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
             return self.user_phoneme_canvas.create_polygon(points, **kwargs, smooth=True)

        my_rectangle_user = round_rectangle_user(0, 0, 600, 100, radius=40, fill=self.box_color)
        self.user_phoneme_canvas.create_window(300, 70, window=self.phoneme_display)
        
        self.user_play_button = ttk.Button (
            text="▶️Play",
            command=self.recorder.play_recording,
            style="Custom.TButton",
            width=7,
            state="disabled"
        )

        self.user_phoneme_canvas.create_window(550, 50, window=self.user_play_button)

        self.phoneme_label = tk.Label(text="Phonemes", font="Inter 12 bold", fg="#78c2ad", bg=self.box_color)
        self.user_phoneme_canvas.create_window(300, 15, window=self.phoneme_label)

        #### RECORD BUTTON ####
        self.rbtn_canvas = tk.Canvas(self.root, width=50, height=50, borderwidth=0,
                                     highlightthickness=0, bg=self.background)

        
        self.rbtn = ttk.Button (
            text="🟢Record",
            command=self.toggle_recording,
            style="Custom.TButton",
            width=15
        )

        self.rbtn_canvas.create_window(25, 25, window=self.rbtn)

        #### CHECK BUTTON ####
        self.check_canvas = tk.Canvas(self.root, width=50, height=50, borderwidth=0,
                                      highlightthickness=0, bg=self.background)
        
        self.check_button= ttk.Button (
            text="✔️New Phrase",
            command=self.generate,
            style="Custom.TButton",
            width=15
        )

        self.check_canvas.create_window(25, 25, window=self.check_button)

        self.spectrogram_canvas = tk.Canvas(self.root, width=100, height=100, borderwidth=0,
                                           highlightthickness=0, bg="lightblue") 
        self.spectrogram_canvas.create_text(50, 50, text="Spectrogram Area")

        ### Score Box ###
        self.score_canvas = tk.Canvas(self.root, width=100, height=100, borderwidth=0,
                                        highlightthickness=0, bg=self.background)
        
        def round_rectangle_score(x1, y1, x2, y2, radius=25, **kwargs):
             points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
             return self.score_canvas.create_polygon(points, **kwargs, smooth=True)
        
        my_rectangle_score = round_rectangle_score(0, 0, 100, 100, radius=10, fill=self.box_color)

        self.score_canvas.create_text(50, 25, text="Score", font=self.font, fill="black")
        self.score_canvas_text_id = self.score_canvas.create_text(50, 50, text="---", font=self.font, fill="black")
        self.score_canvas.place(x=self.screen_width,y=450)
        
        ### Tutorial GUIs ###
                ### Main Tutorial ###
        self.tutorial_btn_canvas = tk.Canvas(self.root, width=100, height=100, borderwidth=0,
                                      highlightthickness=0, bg=self.background)
        
        def round_rectangle_tutorial(x1, y1, x2, y2, radius=25, **kwargs):
             points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
             return self.tutorial_btn_canvas.create_polygon(points, **kwargs, smooth=True)
        
        my_rectangle_tutorial = round_rectangle_tutorial(0, 0, 100, 100, radius=10, fill=self.box_color)

        self.tutorial_button = ttk.Button(
            text="❔",
            command=self.show_tutorial,
            style="Custom.TButton",
            width=2
        )

        self.tutorial_btn_canvas.create_text(50, 25, text="Tutorial", font=self.font, fill="black")
        self.tutorial_btn_canvas.create_window(50, 50, window=self.tutorial_button)
        self.tutorial_btn_canvas.place(x=self.screen_width/12, y=450)  

        self.t_canvas = tk.Canvas(self.root, background="white", width=self.screen_width/2, height=self.screen_height-150)
        self.t_canvas.create_text(200, 50, text="Tutorial", font="Inter 26 bold", fill="#78c2ad")
        self.t_canvas.create_text(200, 100, text="🎧Listen", font=self.font, fill="black")
        self.t_canvas.create_text(200, 125, text="- Click to listen to target phrase.", font=self.font, fill="black")
        self.t_canvas.create_text(200, 175, text="▶️Play", font=self.font, fill="black")
        self.t_canvas.create_text(200, 200, text="- Click to playback recorded audio.", font=self.font, fill="black")
        self.t_canvas.create_text(200, 250, text="🟢Record", font=self.font, fill="black")
        self.t_canvas.create_text(200, 275, text="- Click to record.", font=self.font, fill="black")
        self.t_canvas.create_text(200, 325, text="✔️New Phrase", font=self.font, fill="black")
        self.t_canvas.create_text(200, 350, text="- Click to generate a new target phrase.", font=self.font, fill="black")

        self.exit_tutorial_btn = ttk.Button(
            text="Exit",
            command=self.hide_tutorial,
            style="Custom.TButton"
        )

                ### Target Phrase GUI ###
        self.target_phrase_tutorial_btn = ttk.Button(
            text="❔",
            command=self.show_target_phrase_tutorial,
            style="Custom.TButton",
            width=2
        )

        self.target_phrase_canvas = tk.Canvas(self.root, background="white", width=self.screen_width/2, height=self.screen_height-150)
        self.target_phrase_canvas.create_text(200, 50, text="Target Phrase", font="Inter 26 bold", fill="#78c2ad")
        self.target_phrase_canvas.create_text(200, 100, text="Before Grading", font=self.font, fill="#78c2ad")
        self.target_phrase_canvas.create_text(200, 125, text="- Text will be highlighted black.", font=self.font, fill="black")
        self.target_phrase_canvas.create_text(200, 150, text="- Your goal is to say the target phrase.", font=self.font, fill="black")
        self.target_phrase_canvas.create_text(200, 175, text="- Click on individual words to hear them." , font=self.font, fill="black")

        self.target_phrase_canvas.create_text(200, 225, text="After Grading", font=self.font, fill="#78c2ad")
        self.target_phrase_canvas.create_text(200, 250, text="- Text will be highlighted green, yellow, or red,",
                                              font=self.font, fill="black")
        self.target_phrase_canvas.create_text(200, 270, text="correct, partialy correct, or incorrect respectivley.",
                                              font=self.font, fill="black")
        self.target_phrase_canvas.create_text(200, 295, text="- Accuracy will be given in the bottom right.", font=self.font, fill="black")
        self.target_phrase_canvas.create_text(200, 320, text="- Click on individual words for feedback", font=self.font, fill="black")
        self.target_phrase_canvas.create_text(200, 340, text="and to see how you performed!", font=self.font, fill="black")

        self.exit_target_phrase_tutorial_btn = ttk.Button(
            text="Exit",
            command=self.hide_target_phrase_tutorial,
            style="Custom.TButton"
        )

        self.gen_text_canvas.create_window(30, 50, window=self.target_phrase_tutorial_btn)


                ### Phoneme GUI ###
        self.phoneme_tutorial_btn = ttk.Button(
            text="❔",
            command=self.show_phoneme_tutorial,
            style="Custom.TButton",
            width=2
        )

        self.phoneme_tutorial_canvas = tk.Canvas(self.root, background="white", width=self.screen_width/2, height=self.screen_height-150)
        self.phoneme_tutorial_canvas.create_text(200, 50, text="Phonemes", font="Inter 26 bold", fill="#78c2ad")
        self.phoneme_tutorial_canvas.create_text(200, 100, text="Phonemes are any of the perceptually distinct", font=self.font, fill="black")
        self.phoneme_tutorial_canvas.create_text(200, 120, text="units of sound in a language that distinguish", font=self.font, fill="black")
        self.phoneme_tutorial_canvas.create_text(200, 140, text="one word for anoter.", font=self.font, fill="black")
        self.phoneme_tutorial_canvas.create_text(200, 190, text="The phonemes shown are from the", font=self.font, fill="black")
        self.phoneme_tutorial_canvas.create_text(200, 210, text="International Phonetic Alphabet (IPA).", font=self.font, fill="black")

        self.exit_phoneme_tutorial_btn = ttk.Button(
            text="Exit",
            command=self.hide_phoneme_tutorial,
            style="Custom.TButton"
        )

        self.user_phoneme_canvas.create_window(30, 50, window=self.phoneme_tutorial_btn)


    ### Tutorial GUI Transitions ###

            ### Main Tutorial ###
    def show_tutorial(self):
        self.tutorial_button.config(command=self.hide_tutorial)
        
        self.disable_buttons()

        self.t_canvas.place(x=self.screen_width/4, y=self.screen_height/6)
        self.t_canvas.create_window(200, 400, window=self.exit_tutorial_btn)
        self.t_canvas.update()
    
    def hide_tutorial(self):
        self.tutorial_button.config(command=self.show_tutorial)
        
        self.enable_buttons()

        self.t_canvas.place_forget()
        self.root.update()
    

            ### Target Phrase Tutorial ###
    def show_target_phrase_tutorial(self):
        self.target_phrase_tutorial_btn.config(command=self.hide_target_phrase_tutorial)
        
        self.disable_buttons()

        self.target_phrase_canvas.place(x=self.screen_width/4, y=self.screen_height/6)
        self.target_phrase_canvas.create_window(200, 400, window=self.exit_target_phrase_tutorial_btn)
        self.target_phrase_canvas.update()
    
    def hide_target_phrase_tutorial(self):
        self.target_phrase_tutorial_btn.config(command=self.show_target_phrase_tutorial)

        self.enable_buttons()

        self.target_phrase_canvas.place_forget()
        self.root.update()

            ### Phoneme Tutorial ###
    def show_phoneme_tutorial(self):
        self.phoneme_tutorial_btn.config(command=self.hide_phoneme_tutorial)

        self.disable_buttons()

        self.phoneme_tutorial_canvas.place(x=self.screen_width/4, y=self.screen_height/6)
        self.phoneme_tutorial_canvas.create_window(200, 400, window=self.exit_phoneme_tutorial_btn)
        self.phoneme_tutorial_canvas.update()
    
    def hide_phoneme_tutorial(self):
        self.phoneme_tutorial_btn.config(command=self.show_phoneme_tutorial)
        
        self.enable_buttons()

        self.phoneme_tutorial_canvas.place_forget()
        self.root.update()

            ### Enable/Disable Buttons ###
    def enable_buttons(self):
        self.speech_btn.config(state="normal")
        self.spectrogram_btn.config(state="normal")
        self.ai_model_btn.config(state="normal")
        self.rbtn.config(state="normal")
        self.check_button.config(state="normal")
        self.gen_play_button.config(state="normal")
        if self.recorder.has_recording():
            self.user_play_button.config(state="normal")

    def disable_buttons(self):
        self.speech_btn.config(state="disabled")
        self.spectrogram_btn.config(state="disabled")
        self.ai_model_btn.config(state="disabled")
        self.rbtn.config(state="disabled")
        self.check_button.config(state="disabled")
        self.gen_play_button.config(state="disabled")
        self.user_play_button.config(state="disabled")

        
    def show_spectrogram(self):
        filename = "pronunciation_user_recording.wav"
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

            plt.close(fig)

        except Exception as e:
            print("Error generating spectrogram:", e)

    def speech_click(self):
        if not self.speech_enable:
            if self.spectrogram_enable:
                self.tab_bar_canvas.move(self.tab_image_id, -150, 0)
                self.disable_spectrogram_ui()
            if self.ai_model_enable:
                self.tab_bar_canvas.move(self.tab_image_id, -300, 0)
                self.disable_ai_model_ui()
            self.enable_speech_ui()
            self.root.update_idletasks()

    def spectrogram_click(self):
        if not self.spectrogram_enable:
            if self.speech_enable:
                self.tab_bar_canvas.move(self.tab_image_id, 150, 0)
                self.disable_speech_ui()
            if self.ai_model_enable:
                self.tab_bar_canvas.move(self.tab_image_id, -150, 0)
                self.disable_ai_model_ui() 
            self.enable_spectrogram_ui()
            self.root.update_idletasks()

    def ai_model_click(self):
        if not self.ai_model_enable:
            if self.speech_enable:
                self.tab_bar_canvas.move(self.tab_image_id, 300, 0)
                self.disable_speech_ui()
            if self.spectrogram_enable:
                self.tab_bar_canvas.move(self.tab_image_id, 150, 0)
                self.disable_spectrogram_ui()
            self.enable_ai_model_ui()
            self.root.update_idletasks()

    def enable_speech_ui(self):
        self.speech_enable = True
        self.recorder.set_callback_and_tag(self.process_audio, "pronunciation")
        self.gen_text_canvas.pack(pady=0)
        self.gen_text_canvas.update()
        self.user_phoneme_canvas.pack(pady=20)
        self.user_phoneme_canvas.update()
        self.rbtn_canvas.pack(pady=0)
        self.rbtn_canvas.update()
        self.check_canvas.pack(pady=20)
        self.check_canvas.update()
        self.tutorial_btn_canvas.place(x=30, y=450)
        self.tutorial_btn_canvas.update()
        self.score_canvas.place(x=630,y=450)
        self.score_canvas.update()
        self.root.update()

    def disable_speech_ui(self):
        self.speech_enable = False
        self.gen_text_canvas.pack_forget()
        self.user_phoneme_canvas.pack_forget()
        self.rbtn_canvas.pack_forget()
        self.check_canvas.pack_forget()
        self.tutorial_btn_canvas.place_forget()
        self.score_canvas.place_forget()
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
        self.recorder.set_callback_and_tag(self.jaide_gui.handle_audio, "grammar_help")
        self.jaide_gui_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.root.update()

    def disable_ai_model_ui(self):
        self.ai_model_enable = False
        self.jaide_gui_frame.pack_forget()
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
        self.user_play_button.config(state="disabled")
        self.score_canvas.itemconfig(self.score_canvas_text_id, text="---", fill="black")

    def toggle_recording(self):
        """Toggle the recording state."""
        if not self.recorder.is_recording():
            self.rbtn.config(text="🔴Stop Recording")
            self.recorder.start_recording()
        else:
            self.recorder.stop_recording()
            self.rbtn.config(text="🟢Record")
            # do not enable untill after processing finished

    def process_audio(self, filename):
        """Processes recorded audio and highlights incorrect phonemes."""
        print("Processing audio:", filename)

        user_text = self.stt_model.transcribe(filename)
        print("Transcription:", user_text)

        user_phonemes = tp.text_to_ipa_phoneme(user_text)
        print("Phonemes:", user_phonemes)

        target_words = self.current_text.split()
        user_words = user_text.split()

        # user didnt even try
        if abs(len(target_words) - len(user_words)) >= 4:
            self.highlight_all_red()
            self.user_play_button.config(state="normal")
            return

        self.error_info = ed.get_pronunciation_score(self.current_text, self.current_phoneme, user_phonemes)
        # create section for accuracy later
        self.highlight_text(self.error_info['incorrect_indices'])
        self.highlight_phonemes(self.error_info['phoneme_indices'])
        self.update_accuracy_label(self.error_info['accuracy'])
        self.user_play_button.config(state="normal")

    def highlight_all_red(self): 
        """Highlight phonemes and text red."""
        # should only be called due to issue with error detection
        self.text_display.config(state="normal")
        self.text_display.tag_remove("correct", "1.0", tk.END)
        self.text_display.tag_remove("partial", "1.0", tk.END) 
        self.text_display.tag_remove("incorrect", "1.0", tk.END)
        self.text_display.tag_add("incorrect", "1.0", tk.END)
        self.text_display.config(state="disabled")

        self.phoneme_display.config(state="normal")
        self.phoneme_display.tag_remove("correct", "1.0", tk.END)
        self.phoneme_display.tag_remove("partial", "1.0", tk.END)
        self.phoneme_display.tag_remove("incorrect", "1.0", tk.END)
        self.phoneme_display.tag_add("incorrect", "1.0", tk.END)
        self.phoneme_display.config(state="disabled")


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

    def update_accuracy_label(self, accuracy):
        self.score_canvas.itemconfig(self.score_canvas_text_id, text=str(round(accuracy, 2)) + "%", 
                                     fill="black", font=self.font)


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

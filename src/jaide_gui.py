import tkinter as tk
from tkinter import ttk
from audio_recorder import AudioRecorder
from jaide import Jaide
from models import WhisperModel
import threading
from models import play_tts


class JaideGUI:
    def __init__(self, parent, recorder):
        self.parent = parent
        self.recorder = recorder
        self.jaide_model = Jaide()
        # loading models is slow we should change to lazy loading
        self.stt_model = WhisperModel()
        self.processing = False
        #### WORK IN PROGRESS ####
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#e9ecef")
        self.style.configure("TLabel", background="#ffffff", foreground="#2E6F40", font=("Inter", 12))
        self.style.configure("Title.TLabel", font=("Inter", 18), foreground="#2E6F40")

        self.style.configure("Primary.TButton", background="#78c2ad", foreground="white")
        self.style.map("Primary.TButton",
            background=[("active", "#91d6c2")])
        
        self.style.configure("Danger.TButton", background="#ff4d4d", foreground="white")
        self.style.map("Danger.TButton",
            background=[("active", "#ff7d7d")])

        self.style.configure("Lavender.TButton",
            background="#B57EDC",
            foreground="white",
            font="Inter 16 bold",)

        self.style.map("Lavender.TButton",
            background=[("active", "#C99EE4")]) 

        self.background = "#e9ecef"
        self.main_background = "white"
        self.top_background = "#e9ecef"
        self.box_color = "#f5f5f5"
        self.title_font = "Inter 20 bold"
        self.font = "Inter 16"
        self.text_fill = "black"
        ####__________________####

        self.container = tk.Frame(parent, bg=self.background)
        self.create_widgets()
        # initial greeting
        self.display_bot_message(self.jaide_model.respond(""), "")
    def create_widgets(self):
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(1, weight=1)

        self.header_frame = ttk.Frame(self.container, style="TFrame")
        self.header_frame.grid(row=0, column=0, pady=(0, 0), sticky="ew")
        self.header_frame.columnconfigure(0, weight=1) 
        self.header_frame.columnconfigure(1, weight=0)  

        self.title = tk.Label(
            self.header_frame,
            text="🎓 Practice with Jaide!",
            font=("Inter", 18),
            foreground="#4a7c6e",
            bg=self.top_background
        )
        self.title.grid(row=0, column=0, pady=(0, 0), sticky="w")

        self.reset_btn = ttk.Button(
            self.header_frame,
            text="↻ Reset",
            command=self.reset_conversation,
            style="Lavender.TButton",
            width=10
        )
        self.reset_btn.grid(row=0, column=1, padx=(5, 0), sticky="e")
        
        self.chat_display = tk.Text(
            self.container,
            bg=self.main_background,
            fg=self.text_fill,
            insertbackground="#eaeaea",
            font=("Inter", 16),
            wrap="word",
            relief="flat",
            height=8,
            undo=True 
        )
        self.chat_display.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="nsew")
        self.chat_display.config(state="disabled")  
        
        self.chat_display.tag_configure("bot", foreground="#2E6F40")
        self.chat_display.tag_configure("user", foreground="#ff9933")
        self.chat_display.tag_configure("feedback", foreground="#2f2f2f")
        self.chat_display.tag_configure("grammar", foreground="#3385ff", font=("Inter", 16, "italic"))
        self.chat_display.tag_configure("transition", foreground="#2f2f2f")
        self.chat_display.tag_configure("question", foreground="#2f2f2f")
        self.chat_display.tag_configure("user-sentence", foreground="orange")
        self.chat_display.tag_configure("correct", foreground="green")  
        self.chat_display.tag_configure("notice", foreground="#2f2f2f")
        self.input_frame = ttk.Frame(self.container, style="TFrame")
        self.input_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.input_frame.columnconfigure(0, weight=1)
        
        self.user_input_field = ttk.Entry(
            self.input_frame,
            font=("Inter", 14)
        )
        self.user_input_field.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 5), ipady=6)
        self.user_input_field.bind("<Return>", self.on_user_input)

        self.recording = False
        self.record_btn = ttk.Button(
            self.input_frame,
            text="Start Recording",
            command=self.toggle_recording,
            style="Primary.TButton",
            width=20
        )
        self.record_btn.grid(row=1, column=0, sticky="ew", ipady=0)

        self.loading_label = ttk.Label(
            self.input_frame,
            text="●  ○  ○",
            font=("Courier", 12),
            foreground="#91d6c2",
            anchor="center",
            justify="center"
        )
        self.loading_label.grid(row=1, column=0, sticky="ew", ipady=6)
        self.loading_label.grid_remove()

    def toggle_recording(self):
        if self.processing:
            return
        if not self.recorder.is_recording():
            self.record_btn.config(text="Stop Recording", style="Danger.TButton")
            self.recorder.start_recording()
        else:
            self.record_btn.config(text="Start Recording", style="Primary.TButton")
            self.recorder.stop_recording()

    def reset_conversation(self):
        if self.processing:
            return
            
        self.jaide_model.reset_conversation()
        
        self.chat_display.config(state="normal")
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state="disabled")
        
        self.user_input_field.delete(0, tk.END)
        self.user_input_field.focus()
        self.display_bot_message(self.jaide_model.respond(""), "")

    def on_user_input(self, event=None):
        user_input = self.user_input_field.get().strip()
        self.user_input_field.delete(0, tk.END)
        if self.processing or not user_input:
            return

        self.user_input_field.config(state="disabled")

        if user_input.lower().startswith("help me pronounce"):
            self.display_user_message(user_input)
            word = user_input[len("help me pronounce "):].strip()
            cleaned_word = word.strip('.,!?"\' \t\n')
            pronunciation_message, question_message = self.jaide_model.get_pronunciation_help(cleaned_word)
            self.display_pronunciation_help(pronunciation_message, question_message, word)
        else:
            self.processing = True
            self.parent.after(0, self.start_loading_animation)
            def process():
                self.display_user_message(user_input)
                response_data = self.jaide_model.respond(user_input)
                self.parent.after(0, lambda: self.finish_processing(response_data, user_input))
            threading.Thread(target=process, daemon=True).start()
            
    def start_loading_animation(self):
        self.loading_label.grid()
        self.record_btn.grid_remove()
        self.loading_animation_index = 0
        self.loading_animation_running = True
        self.animate_loading_dots()

    def animate_loading_dots(self):
        if not self.loading_animation_running:
            return

        frames = [
            "⬤   ●   ●",
            "●   ⬤   ●",
            "●   ●   ⬤"
        ]

        self.loading_label.config(
            text=frames[self.loading_animation_index],
            font=("Courier", 16),
            foreground="#91d6c2",
            anchor="center"
        )
        self.loading_animation_index = (self.loading_animation_index + 1) % len(frames)
        self.parent.after(250, self.animate_loading_dots)

    def stop_loading_animation(self):
        self.loading_animation_running = False
        self.loading_label.grid_remove()
        self.record_btn.grid()

    def stop_loading_animation(self):
        self.loading_animation_running = False
        self.loading_label.grid_remove()
        self.record_btn.grid()

    def handle_audio(self, filename):
        self.processing = True
        self.parent.after(0, self.start_loading_animation)

        def process():
            user_sentence = self.stt_model.transcribe(filename)
            self.display_user_message(user_sentence)
            response_data = self.jaide_model.respond(user_sentence)
            self.parent.after(0, lambda: self.finish_processing(response_data, user_sentence))

        threading.Thread(target=process, daemon=True).start()

    def finish_processing(self, response_data, user_sentence):
        self.display_bot_message(response_data, user_sentence)
        self.user_input_field.config(state="normal")
        self.processing = False
        self.stop_loading_animation()

    def display_pronunciation_help(self, pronunciation_message, question_message, word):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, "jaide: ", ("bot",))
        self.chat_display.insert(tk.END, pronunciation_message + "\n")
        self.chat_display.insert(tk.END, f"Click to hear how to say {word}: ")
        self.chat_display.insert(tk.END, "▶\n", ("play_word"))
        self.chat_display.insert(tk.END, question_message + "\n\n")

        self.chat_display.tag_config("play_word", foreground="#B57EDC")
        self.chat_display.tag_bind("play_word", "<Button-1>", lambda e, word=word: self.play_word_tts(word))
        self.chat_display.config(state="disabled")
        self.chat_display.yview(tk.END)
        self.user_input_field.config(state="normal")
        

    def display_bot_message(self, response_data, user_sentence):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, "jaide: ", ("bot",))
        response, edited_sentence = response_data
        
        if isinstance(response, str):
            # when the ai asks for name
            self.chat_display.insert(tk.END, response + "\n\n")
        else:
            if "response_comment" in response:
                self.chat_display.insert(tk.END, response["response_comment"], ("feedback",))

            if "grammar" in response and response["grammar"]:
                self.chat_display.insert(tk.END, f" I noticed a few spots we could polish.\n\n Instead of '", ("notice",))
                self.chat_display.insert(tk.END, f"{user_sentence}", ("user-sentence")) 
                self.chat_display.insert(tk.END, "'\n try saying: '", ("notice",))

                self.chat_display.insert(tk.END, f"{edited_sentence}", ("correct"))
                self.chat_display.insert(tk.END, "' \n", ("notice",))

                self.chat_display.insert(tk.END, " Heres some in-depth feedback:\n", ("transition",)) # JAYDEN CHNGE THIS
                for line in response["grammar"]:
                    self.chat_display.insert(tk.END, f"• {line}\n", ("grammar",))
            else:
                self.chat_display.insert(tk.END, " ✅ Your response is grammatically correct! ", ("correct",))
           
            if "transition" in response:
                self.chat_display.insert(tk.END, "\n" + response["transition"] + " ", ("transition",))

            if "question" in response:
                self.chat_display.insert(tk.END, response["question"] + "\n\n", ("question",))

        self.chat_display.config(state="disabled")
        self.chat_display.yview(tk.END)
    
    def play_word_tts(self, word):
        play_tts(word)

    def display_user_message(self, message):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, "You: ", ("user",))
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.config(state="disabled")
        self.chat_display.yview(tk.END)
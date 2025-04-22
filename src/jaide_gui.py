import tkinter as tk
from tkinter import ttk
from audio_recorder import AudioRecorder
from jaide import Jaide
from models import WhisperModel
import threading

# TODO: add a button to reset text
#       then call reset on JAIDE
class JaideGUI:
    def __init__(self, parent, recorder):
        self.parent = parent
        self.recorder = recorder
        self.jaide_model = Jaide()
        # loading models is slow perhaps threading?
        self.stt_model = WhisperModel()
        self.processing = False
        #### WORK IN PROGRESS ####
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#ffffff")
        self.style.configure("TLabel", background="#ffffff", foreground="#2E6F40", font=("Inter", 12))
        self.style.configure("Title.TLabel", font=("Inter", 18), foreground="#2E6F40")

        self.style.configure("Primary.TButton", background="#78c2ad", foreground="white")
        self.style.map("Primary.TButton",
            background=[("active", "#91d6c2")])
        
        self.style.configure("Danger.TButton", background="#ff4d4d", foreground="white")
        self.style.map("Danger.TButton",
            background=[("active", "#ff7d7d")])

        self.background = "white"
        self.box_color = "#f5f5f5"
        self.title_font = "Inter 20 bold"
        self.font = "Inter 16"
        self.text_fill = "black"
        ####__________________####

        self.container = tk.Frame(parent, bg=self.background)
        self.create_widgets()

    def create_widgets(self):
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(1, weight=1)

        self.title = tk.Label(
            self.container,
            text="🎓 Practice with jaide!",
            font=("Inter", 18),
            foreground="#2E6F40"
        )
        self.title.grid(row=0, column=0, pady=(0, 0), sticky="ew")

        self.chat_display = tk.Text(
            self.container,
            bg=self.background,
            fg=self.text_fill,
            insertbackground="#eaeaea",
            font=("Inter", 16),
            wrap="word",
            relief="flat",
        )
        self.chat_display.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="nsew")
        self.chat_display.config(state="disabled")
        #### TAG HIGHLIGHTING #### I will clean this later

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

        self.recording = False
        self.record_btn = ttk.Button(
            self.input_frame,
            text="🎙️ Start Recording",
            command=self.toggle_recording,
            style="Primary.TButton",
            width=20
        )
        self.record_btn.grid(row=0, column=0, sticky="ew", ipady=6)
        self.loading_label = ttk.Label(
        self.input_frame,
        text="●  ○  ○",
        font=("Courier", 12),
        foreground="#91d6c2",
        anchor="center",
        justify="center"
        )

        self.loading_label.grid(row=0, column=0, sticky="ew", ipady=6)
        self.loading_label.grid_remove()
        # initial message
        self.display_bot_message("Hi there! I'm here to help you learn English. Let's have a conversation to help you practice your English. What's your name?", "", "")

    def toggle_recording(self):
        if self.processing:
            return
        if not self.recorder.is_recording():
            self.record_btn.config(text="⏹️ Stop Recording", style="Danger.TButton")
            self.recorder.start_recording()
        else:
            self.record_btn.config(text="🎙️ Start Recording", style="Primary.TButton")
            self.recorder.stop_recording()

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
            response, edited_sentence = self.jaide_model.respond(user_sentence)
            self.parent.after(0, lambda: self.finish_processing(response, user_sentence, edited_sentence))

        threading.Thread(target=process, daemon=True).start()

    def finish_processing(self, response, user_sentence, edited_sentence):
        self.display_user_message(user_sentence)
        self.display_bot_message(response, user_sentence, edited_sentence)
        self.processing = False
        self.stop_loading_animation()

    def display_bot_message(self, response_data, user_sentence, edited_sentence):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, "jaide: ", ("bot",))

        if isinstance(response_data, str):
            # when the ai asks for name
            self.chat_display.insert(tk.END, response_data + "\n\n")
        else:
            if "feedback" in response_data:
                self.chat_display.insert(tk.END, response_data["feedback"], ("feedback",))

            if "grammar" in response_data and response_data["grammar"]:
                self.chat_display.insert(tk.END, f" I noticed a few spots we could polish.\n\n Instead of '", ("notice",))
                self.chat_display.insert(tk.END, f"{user_sentence}", ("user-sentence")) 
                self.chat_display.insert(tk.END, "'\n try saying: '", ("notice",))

                self.chat_display.insert(tk.END, f"{edited_sentence}", ("correct"))
                self.chat_display.insert(tk.END, "' \n", ("notice",))

                self.chat_display.insert(tk.END, " Heres some in-depth feedback:\n", ("transition",)) # JAYDEN CHNGE THIS
                for line in response_data["grammar"]:
                    self.chat_display.insert(tk.END, f"         • {line}\n", ("grammar",))
            else:
                self.chat_display.insert(tk.END, " ✅ Your response is grammatically correct! ", ("correct",))
           
            if "transition" in response_data:
                self.chat_display.insert(tk.END, "\n" + response_data["transition"] + " ", ("transition",))

            if "question" in response_data:
                self.chat_display.insert(tk.END, response_data["question"] + "\n\n", ("question",))

        self.chat_display.config(state="disabled")
        self.chat_display.yview(tk.END)

    def display_user_message(self, message):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, "You: ", ("user",))
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.config(state="disabled")
        self.chat_display.yview(tk.END)
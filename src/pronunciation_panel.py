import tkinter as tk
from tkinter import ttk
import sys
import os
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from res.descriptions import DESCRIPTIONS, AFFIRMATIONS
from error_detection import IPA_MAPPINGS


class PronunciationPanel:
    def __init__(self, parent, tts_callback=None):
        self.parent = parent
        self.is_visible = False
        self.panel_width = 300 
        self.panel_height = 400 # i think fixed sizing fine for this.
        self.tts_callback = tts_callback
        # USE TTK FOR CONSISTENCY PLS
        self.style = ttk.Style()
        self.style.theme_use('clam')  # only clam or alt work :(
        
        #### STYLE CONFIGURATION ####
        self.style.configure("Dark.TFrame", background='#1e1e1e')
        self.style.configure("Dark.TLabel", background='#1e1e1e', foreground='#eaeaea')
        self.style.configure("Separator.TLabel", background='#1e1e1e',foreground='#eaeaea', font=("Inter", 24))
        self.style.configure("AudioIcon.TLabel", background='#1e1e1e', foreground='#ff4d4d', font=("Segoe UI Emoji" if sys.platform == 'win32' else "Arial", 20))
        self.style.configure("ScrollIndicator.TLabel", background='#1e1e1e', foreground='#666666', font=("Inter", 10))
        
        # create main container with ttk
        self.container = tk.Frame(
            self.parent, 
            bg='#1e1e1e',
            width=self.panel_width, 
            height=self.panel_height
        )
        self.container.pack_propagate(False) 

        self.border_frame = tk.Frame(
            self.container,
            bg='#444444',
            width=self.panel_width,
            height=self.panel_height
        )
        self.border_frame.place(x=0, y=0)
        
        self.inner_frame = tk.Frame(
            self.border_frame,
            bg="#1e1e1e",
            width=self.panel_width-2,
            height=self.panel_height-2
        )
        self.inner_frame.place(x=1, y=1)
        self.inner_frame.pack_propagate(False)
        
        ##### UI WIDGETS #####
        self.create_widgets()
        
        # NOTE: dont bind outside click here
        self.parent.update_idletasks()
    
    def create_widgets(self):
        self.top_frame = tk.Frame(self.inner_frame,  bg='#1e1e1e')
        self.top_frame.pack(fill="x", pady=(15, 15), padx=15)
        
        # audio icon always in top right
        self.audio_icon = tk.Label(
            self.top_frame,
            text='🔊', # lazy pls change to image
        )
        self.audio_icon.pack(side="right")
        
        self.word_frame = tk.Frame(self.top_frame, bg="#1e1e1e")
        self.word_frame.pack(side="top", fill="x", anchor="w")
        
        self.text_display = tk.Text(
            self.word_frame,
            height=1,
            width=20,  # i resize this based on char count 
            font=("Inter", 24, "bold"),
            bg='#1e1e1e',
            fg='#F9F6EE',
            relief="flat",
            highlightthickness=0,
            padx=0,
            pady=0
        )
        self.text_display.pack(side="left", fill="x")
        
        # tags for text highlighting
        self.text_display.tag_configure("correct", foreground='#4CAF50')
        self.text_display.tag_configure("partial", foreground='#ff9933') 
        self.text_display.tag_configure("incorrect", foreground='#ff4d4d')  

        self.text_display.config(state="disabled")

        self.phoneme_frame = tk.Frame(self.top_frame, bg="#1e1e1e")
        
        self.phoneme_display = tk.Text(
            self.phoneme_frame,
            height=1,
            width=20, # again resize this later
            font=("Inter", 24),
            bg='#1e1e1e',
            fg='#F9F6EE',
            relief="flat",
            highlightthickness=0,
            padx=0,
            pady=0,
            wrap="word"
        )
        self.phoneme_display.pack(side="left", fill="x", expand=True)
        self.phoneme_display.tag_configure("correct", foreground='#4CAF50')
        self.phoneme_display.tag_configure("partial", foreground='#ff9933')
        self.phoneme_display.tag_configure("incorrect", foreground='#ff4d4d')

        self.phoneme_display.config(state="disabled")
    
        # top from bottom section
        divider = ttk.Separator(self.inner_frame, orient="horizontal")
        divider.pack(fill="x", pady=(0, 15), padx=15)
        
        self.scroll_frame = tk.Frame(self.inner_frame, bg='#1e1e1e')
        self.scroll_frame.pack(fill="both", expand=True, padx=15)

        self.scrollbar = ttk.Scrollbar(self.scroll_frame, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")
        
        # canvas for scrollable content
        self.canvas = tk.Canvas(
            self.scroll_frame,
            bg='#1e1e1e',
            highlightthickness=0,
            height=280,
            yscrollcommand=self.scrollbar.set
        )
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar.config(command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#1e1e1e')

        self.canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.scrollable_frame, 
            anchor="nw",
            width=self.panel_width-45
        )

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scroll_indicator = tk.Label(
            self.inner_frame,
            text="▼ Scroll for more",
        )

    def display_phoneme_with_tags(self, phonemes):
        self.phoneme_display.config(state="normal")
        self.phoneme_display.delete("1.0", tk.END)
        # start slash
        self.phoneme_display.insert("1.0", "/")
        
        char_pos = 1  # i prepend a slash character
        for phoneme_data in phonemes:
            phoneme = phoneme_data['phoneme']
            severity = phoneme_data['severity']
            # building the string
            self.phoneme_display.insert(f"1.0 + {char_pos}c", phoneme)
            # apply tags
            tag_start = f"1.0 + {char_pos}c"
            tag_end = f"1.0 + {char_pos + len(phoneme)}c"
            self.phoneme_display.tag_add(severity, tag_start, tag_end)
            # update character position
            char_pos += len(phoneme)
        
        # end slash
        self.phoneme_display.insert(f"1.0 + {char_pos}c", "/")
        
        # Configure display width based on content
        self.phoneme_display.config(width=char_pos + 1)  # +1 for the ending slash
        self.phoneme_display.config(state="disabled")


    def display_word_with_tags(self, phonemes, word):
        self.text_display.config(state="normal")
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert("1.0", word)
        self.text_display.config(width=len(word))
        self.text_display.tag_add("correct", "1.0", tk.END)
        # Map phonemes to character positions in the word
        char_pos = 0
        for phoneme_data in phonemes:
            phoneme = phoneme_data['phoneme']
            severity = phoneme_data['severity']
            # character count this phoneme represents
            char_count = IPA_MAPPINGS.get(phoneme, 1)
            # apply tag
            tag_start = f"1.0 + {char_pos}c"
            tag_end = f"1.0 + {char_pos + char_count}c"
            print("highlighting word", severity)
            self.text_display.tag_add(severity, tag_start, tag_end)
            # update starting char position
            char_pos += char_count
        
        self.text_display.config(state="disabled")

    def clear_feedback_items(self):
        for child in self.scrollable_frame.winfo_children():
            child.destroy()

    def _on_mousewheel(self, event):
        if self.is_visible:
            delta = -1 * (event.delta // 120) 
            self.canvas.yview_scroll(delta, "units")
            self.update_scroll_indicator()
            return "break"

    def update_scroll_indicator(self):
        yview = self.canvas.yview()
        if yview[1] < 1.0:
            self.scroll_indicator.pack(side="bottom", pady=5)
        else:
            self.scroll_indicator.pack_forget()


    def add_feedback_item(self, phoneme, description, color):
        # container for each one
        item_frame = tk.Frame(self.scrollable_frame, bg="#1e1e1e")
        item_frame.pack(fill="x", pady=(0, 15))
        
        style_name = f"Phoneme{color.replace('#', '')}.TLabel"
        self.style.configure(style_name, background='#1e1e1e', foreground=color, font=("Inter", 18, "bold"))

        phoneme_label = ttk.Label(
            item_frame,
            text=f"/{phoneme}/",
            style=style_name
        )
        phoneme_label.pack(anchor="w")
        
        desc_style = f"Desc{color.replace('#', '')}.TLabel"
        self.style.configure(desc_style, background='#1e1e1e', foreground="white", font=("Inter", 12))
        # description label
        desc_label = ttk.Label(
            item_frame,
            text=description,
            style=desc_style,
            wraplength=220
        )
        desc_label.pack(anchor="w", pady=(5, 0))
        
    def update_content(self, word, phonemes):
        self.display_word_with_tags(phonemes, word)
        self.display_phoneme_with_tags(phonemes)
        self.audio_icon.bind("<Button-1>", lambda e: self.play_word_tts(word))
        self.parent.update_idletasks()
        self.phoneme_frame.pack_forget()
        
        # check if we can fit phonemes on the same line as the word
        word_width = self.text_display.winfo_width()
        available_width = self.panel_width - word_width - self.audio_icon.winfo_width() - 10
        phoneme_width = self.phoneme_display.winfo_reqwidth()
        
        if phoneme_width < available_width:
            # add phonemes to the same line as word
            self.phoneme_frame.pack(in_=self.word_frame, side="left", padx=3)
        else:
            self.phoneme_frame.pack(side="top", anchor="w", pady=(5, 0))
        
        # adding feedback to panel
        self.clear_feedback_items()
        for phoneme_data in phonemes:
                phoneme = phoneme_data['phoneme']
                severity = phoneme_data['severity']
                color = "#4CAF50"
                if severity == "incorrect":
                    color = "#ff4d4d" 
                elif severity == "partial":
                    color = "#ff9933"
                # Get description for the phoneme
                description = self.get_phoneme_description(phoneme, severity)
                self.add_feedback_item(phoneme, description, color)

        self.scrollable_frame.update_idletasks()  
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.update_scroll_indicator()

    def get_phoneme_description(self, phoneme, severity):
        if severity == "correct":
            return random.choice(AFFIRMATIONS)
        description = DESCRIPTIONS.get(phoneme, 
        f"The /{phoneme}/ sound needs attention. A {severity} error was detected.")

        if severity == "partial":
            description = "Close! " + description
        return description

    def play_word_tts(self, word):
        self.tts_callback(word)

    def bind_outside_click(self):
        # store the original binding so we can unbind it later
        self.outside_click_binding = self.parent.bind("<Button-1>", self.check_outside_click, add="+")

    def unbind_outside_click(self):
        if hasattr(self, 'outside_click_binding'):
            self.parent.unbind("<Button-1>", self.outside_click_binding)

    def show(self, x, y, word, phonemes):
        # UPDATE FIRST
        self.update_content(word, phonemes)
        # bring front
        self.container.lift() 
        self.parent.update_idletasks()
    
        window_width = self.parent.winfo_width()
        window_height = self.parent.winfo_height()
        x = max(0, min(x, window_width - self.panel_width))
        y = max(0, min(y, window_height - self.panel_height))
        
        # reset scroll position to top
        self.canvas.yview_moveto(0)
        self.update_scroll_indicator()
        self.parent.update_idletasks()
        # show panel at cursor position
        self.container.place(x=x, y=y)
        self.is_visible = True
        # add binding for outside clicks - IMPORTANT: do this AFTER showing the panel 
        self.parent.after(100, self.bind_outside_click)
        self.parent.update_idletasks()
        
        # update childs
        for child in self.scrollable_frame.winfo_children():
            child.update_idletasks()
        
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def hide(self):
        if self.is_visible:
            # remove the outside click binding first
            self.unbind_outside_click()
            self.container.place_forget()
            self.is_visible = False

    def check_outside_click(self, event):
        if not self.is_visible:
            return
        # checks if click is in panel
        container = self.container
        widget = event.widget
        if widget == container or self.is_child_of(widget, container):
            return
        
        self.hide()

    def is_child_of(self, widget, parent):
        while widget:
            if widget == parent:
                return True
            widget = widget.master
        return False
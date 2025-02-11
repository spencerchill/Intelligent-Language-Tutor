import tkinter as tk
from tkinter import Frame
from text_gen import gen_random_text

def app():
    
    curText = gen_random_text()

    root = tk.Tk()
    root.title("ILT")
    root.geometry("800x600")

    textLabel = tk.Label(root, text=curText)

    def generate():
        curText = gen_random_text()
        textLabel.config(text=curText)

    rbtn = tk.Button(root, text="Record", command=root.destroy)
    generateBtn = tk.Button(root, text="Generate New Text", 
                            command=generate)

    textLabel.pack(padx='20', pady='40', side="top")

    generateBtn.pack(padx='20', pady='40', side='bottom')
    rbtn.pack(padx='20',pady='40', side="bottom")

    root.mainloop()

if __name__ == "__main__":
    app()


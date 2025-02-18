import tkinter as tk
from text_gen import gen_random_text
from text_processing import text_to_ipaPhoneme

def app():
    root = tk.Tk()
    root.title("ILT")
    root.geometry("800x600")

    # Initial Text and Phoneme Generation
    curText = gen_random_text()
    currentPhoneme = text_to_ipaPhoneme(curText)

    # Labels for Text and Phonemes
    textLabel = tk.Label(root, text=curText, font=("Arial", 14))
    phonemeLabel = tk.Label(root, text=currentPhoneme, font=("Arial", 12), fg="blue")

    def generate():
        """Generates new text and updates both labels."""
        nonlocal curText  # Ensure we update the outer scope variable
        curText = gen_random_text()
        currentPhoneme = text_to_ipaPhoneme(curText)
        textLabel.config(text=curText)
        phonemeLabel.config(text=currentPhoneme)

    # Buttons
    rbtn = tk.Button(root, text="Record", command=root.destroy, bg="red", fg="white")
    generateBtn = tk.Button(root, text="Generate New Text", command=generate, bg="green", fg="white")

    # Layout
    textLabel.pack(padx=20, pady=20, side="top")
    phonemeLabel.pack(padx=20, pady=10, side="top")
    generateBtn.pack(padx=20, pady=20, side="bottom")
    rbtn.pack(padx=20, pady=20, side="bottom")

    root.mainloop()

if __name__ == "__main__":
    app()


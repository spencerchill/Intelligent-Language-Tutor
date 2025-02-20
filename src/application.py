import tkinter as tk
from text_gen import gen_random_text
from text_processing import text_to_ipaPhoneme

#recording imports
import pyaudio 
import wave 
import threading
import os

class Application:
    def __init__(self):
        pass

    def app(self):

        # Constants for audio recording
        FORMAT = pyaudio.paInt16  
        CHANNELS = 1  
        RATE = 44100  
        CHUNK = 1024  
        i = 1
        OUTPUT_FILENAME = (f"ILT_Audio{i}.wav")

        # Recording state variables
        global is_recording
        is_recording = False
        frames = []
        audio = pyaudio.PyAudio()
        stream = None  # Define the stream globally to avoid scope issues

        def record_audio():
            """ Function to record audio in a separate thread """
            global is_recording, frames, stream

            stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                                input=True, frames_per_buffer=CHUNK)
            
            frames = []
            print("Recording started...")
            
            while is_recording:
                try:
                    data = stream.read(CHUNK)
                    frames.append(data)
                except Exception as e:
                    print(f"Error recording audio: {e}")
                    break

            print("Recording stopped.")

            # Stop and close the stream
            stream.stop_stream()
            stream.close()

            exists = True
            i = 1
            while exists:
                if os.path.exists(f"ILT_Audio{i}.wav"):
                    i += 1
                else:
                    OUTPUT_FILENAME = (f"ILT_Audio{i}.wav")
                    exists = False
            # Save the recording to a WAV file
            with wave.open(OUTPUT_FILENAME, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            print(f"Audio file saved as {OUTPUT_FILENAME}")

        def toggle_recording():
            """ Toggle the recording state when the button is pressed """
            global is_recording

            if not is_recording:
                is_recording = True
                rbtn.config(text="Stop Recording", bg="red")

                # Start recording in a separate thread
                threading.Thread(target=record_audio, daemon=True).start()
            
            else:
                is_recording = False
                rbtn.config(text="Start Recording", bg="green")


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
        rbtn = tk.Button(root, text="Start Recording", command=toggle_recording)
        generateBtn = tk.Button(root, text="Generate New Text", command=generate)

        # Layout
        textLabel.pack(padx=20, pady=20, side="top")
        phonemeLabel.pack(padx=20, pady=10, side="top")
        generateBtn.pack(padx=20, pady=20, side="bottom")
        rbtn.pack(padx=20, pady=20, side="bottom")

        root.mainloop()

if __name__ == "__main__":
    app=Application()
    app.app()

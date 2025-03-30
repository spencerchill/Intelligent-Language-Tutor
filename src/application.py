import tkinter as tk
from text_gen import gen_random_text
import text_processing as tp
import error_detection as ed
import models as md
import string # punctuation removal
#recording imports
import pyaudio
import wave
import threading
import os

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
           # process audio now that recording is stopped
           threading.Thread(target=process_audio, args=(OUTPUT_FILENAME,), daemon=True).start()
     
       def highlight_text(incorrect_indices, total_length):
           """Highlight incorrect letters in the text"""
           text_display.config(state="normal")
           text_display.tag_remove("incorrect", "1.0", tk.END)  # previous highlights
           text_display.tag_remove("correct", "1.0", tk.END)


           text_display.tag_add("correct", "1.0", f"1.{total_length}") # entire text is green first


           for index in incorrect_indices:
               text_display.tag_add("incorrect", f"1.{index}", f"1.{index+1}")


           text_display.config(state="disabled")
         
       def process_audio(filename):
           """Analyze pronunciation from audio."""
           print("Processing audio:", filename)
           # convert speech to text
           user_text = md.STTModel().transcribe(filename)
           print("Transcription: ", user_text)
           # convert text to phonemes
           user_phonemes = tp.text_to_ipa_phoneme(user_text)
           print("Phonemes: ", user_phonemes)
           # get pronunciation info, such as accuracy and incorrect indices
           error_info = ed.get_pronunciation_score(current_text, tp.text_to_ipa_phoneme(current_text), user_phonemes)
           print("Pronunciation info:", error_info)
         
           highlight_text(error_info['incorrect_indices'], len(current_text))

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
       # GUI
       root = tk.Tk()
       root.configure(bg="white")
       root.title("ILT")
       root.geometry("800x600")
       # my app looks awful on mac as colors are not standardized. feel free to delete when you set a style \
       root.option_add('*Background', 'white')
       root.option_add('*Foreground', 'black')
       root.option_add('*TButton*Background', 'white')
       root.option_add('*TButton*Foreground', 'white')
       root.option_add('*TLabel*Background', 'white')
       root.option_add('*TLabel*Foreground', 'black')

       # Initial Text and Phoneme Generation
       # removing punctuation for error detection (working on it)
       current_text = ''.join([char for char in gen_random_text() if char not in string.punctuation])
       current_phoneme = tp.text_to_ipa_phoneme(current_text)
       # Labels for Text and Phonemes
       # changed textlabel to textdisplay for highlighting
       # also keep style consistent pls
       text_display = tk.Text(root, font=("Arial", 14), wrap="word", width=40, height=4) # change options how you see fit
       text_display.insert("1.0", current_text)
       text_display.config(state="disabled") 
       text_display.tag_config("correct", foreground="green")
       text_display.tag_config("incorrect", foreground="red")
  
       phoneme_label = tk.Label(root, text=current_phoneme, font=("Arial", 12), fg="blue")
       #=currentPhoneme, font=("Arial", 12), fg="blue")

       def generate():
           """Generates new text and updates both labels."""
           nonlocal current_text  # Ensure we update the outer scope variable
           # removing punctuation for error detection (working on it)
           current_text = ''.join([char for char in gen_random_text() if char not in string.punctuation])
           current_phoneme = tp.text_to_ipa_phoneme(current_text)

           text_display.config(state="normal")
           text_display.delete("1.0", tk.END)
           text_display.insert("1.0", current_text)
           text_display.config(state="disabled")

           phoneme_label.config(text=current_phoneme)

       # Buttons
       rbtn = tk.Button(root, text="Start Recording", command=toggle_recording)
       generate_btn = tk .Button(root, text="Generate New Text", command=generate)

       # Layout
       text_display.pack(padx=20, pady=20)
       phoneme_label.pack(padx=20, pady=10, side="top")
       generate_btn.pack(padx=20, pady=20, side="bottom")
       rbtn.pack(padx=20, pady=20, side="bottom")
      
       root.mainloop()

if __name__ == "__main__":
   app=Application()
   app.app()
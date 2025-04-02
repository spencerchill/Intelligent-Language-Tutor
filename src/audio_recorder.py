import pyaudio
import wave
import threading
import os
from pydub import AudioSegment
from pydub.playback import play

class AudioRecorder:
    def __init__(self, callback):
        self._is_recording = False
        self.audio = pyaudio.PyAudio()
        # avoid circular dependency between app and recorder
        self.callback = callback
        self.filename = None

    def play_recording(self):
        """Play the last recorded audio file."""
        if self.filename and os.path.exists(self.filename):
            def _play():
                audio = AudioSegment.from_wav(self.filename)
                play(audio)
            threading.Thread(target=_play, daemon=True).start()

    def is_recording(self):
        return self._is_recording

    def start_recording(self):
        if self._is_recording:
            return
        self._is_recording = True
        threading.Thread(
                    target=self.record_audio,
                    daemon=True,
                ).start()

    def stop_recording(self):
        self._is_recording = False

    def record_audio(self):
        """Prepare recording"""
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024

        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        frames = []
        
        print("Recording started...")
        while self._is_recording:
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

        
        self.filename = f"user_recording.wav"
        # Save the recording to a WAV file
        with wave.open(self.filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))

        print(f"Audio file saved as {self.filename}")
        # process audio now that recording is stopped
        threading.Thread(
            target=self.callback, args=(self.filename,), daemon=True
        ).start()

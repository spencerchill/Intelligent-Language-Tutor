import pyaudio
import wave
import threading
import os


class AudioRecorder:
    def __init__(self, callback):
        self._is_recording = False
        self.audio = pyaudio.PyAudio()
        # avoid circular dependency between app and recorder
        self.callback = callback
        self.OUTPUT_FILENAME = None

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

        i = 1
        while os.path.exists(f"ILT_Audio{i}.wav"):
            i += 1
        self.OUTPUT_FILENAME = f"ILT_Audio{i}.wav"
        # Save the recording to a WAV file
        with wave.open(self.OUTPUT_FILENAME, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b"".join(frames))

        print(f"Audio file saved as {self.OUTPUT_FILENAME}")
        # process audio now that recording is stopped
        threading.Thread(
            target=self.callback, args=(self.OUTPUT_FILENAME,), daemon=True
        ).start()

import pyaudio
import wave
import speech_recognition as sr
import sys
import threading
from tkinter import *
from tkinter.scrolledtext import ScrolledText

class TranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Transcription")
        self.root.geometry("600x400")
        
        # Create GUI elements
        self.text_area = ScrolledText(root, wrap=WORD, state='disabled')
        self.text_area.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        self.button_frame = Frame(root)
        self.button_frame.pack(fill=X, padx=10, pady=5)
        
        self.start_button = Button(self.button_frame, text="Start", command=self.start_recording)
        self.start_button.pack(side=LEFT, padx=5)
        
        self.stop_button = Button(self.button_frame, text="Stop", command=self.stop_recording, state=DISABLED)
        self.stop_button.pack(side=LEFT, padx=5)
        
        self.clear_button = Button(self.button_frame, text="Clear", command=self.clear_text)
        self.clear_button.pack(side=RIGHT, padx=5)
        
        self.status_label = Label(root, text="Status: Stopped", fg="red")
        self.status_label.pack(side=BOTTOM, pady=5)
        
        self.recording = False
        self.audio_file = "recording.wav"
        
    def start_recording(self):
        self.recording = True
        self.start_button.config(state=DISABLED)
        self.stop_button.config(state=NORMAL)
        self.status_label.config(text="Status: Recording...", fg="green")
        self.recording_thread = threading.Thread(target=self.record_loop)
        self.recording_thread.start()
        
    def stop_recording(self):
        self.recording = False
        self.start_button.config(state=NORMAL)
        self.stop_button.config(state=DISABLED)
        self.status_label.config(text="Status: Stopped", fg="red")
        
    def clear_text(self):
        self.text_area.config(state='normal')
        self.text_area.delete(1.0, END)
        self.text_area.config(state='disabled')
        
    def record_loop(self):
        while self.recording:
            self.record_audio(self.audio_file)
            self.transcribe_audio(self.audio_file)
            
    def record_audio(self, filename, record_seconds=5):
        # Audio configuration
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024
        
        audio = pyaudio.PyAudio()
        
        # Start recording
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
        
        print("Recording...")
        frames = []
        
        for _ in range(0, int(RATE / CHUNK * record_seconds)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("Finished recording")
        
        # Stop recording
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save audio to file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    def transcribe_audio(self, filename):
        recognizer = sr.Recognizer()
        with sr.AudioFile(filename) as source:
            audio = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio)
            self.text_area.config(state='normal')
            self.text_area.insert(END, f"{text}\n")
            self.text_area.config(state='disabled')
            self.text_area.see(END)
        except sr.UnknownValueError:
            self.text_area.config(state='normal')
            self.text_area.insert(END, "[Could not understand audio]\n")
            self.text_area.config(state='disabled')
            self.text_area.see(END)
        except sr.RequestError as e:
            self.text_area.config(state='normal')
            self.text_area.insert(END, f"[Error: {e}]\n")
            self.text_area.config(state='disabled')
            self.text_area.see(END)

if __name__ == "__main__":
    root = Tk()
    app = TranscriptionApp(root)
    root.mainloop()

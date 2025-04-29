import pyaudio
import wave
import requests
import base64
import time
import webrtcvad
import os
from datetime import datetime

class RealTimeRecognizer:
    def __init__(self, device_index=None, rate=16000, frame_duration=30, vad_aggressiveness=2, lang="STT for course"):
        self.rate = rate
        self.lang = lang
        self.frame_duration = frame_duration  # ms
        self.frame_size = int(rate * frame_duration / 1000)
        self.byte_frame_size = self.frame_size * 2
        self.channels = 1
        self.format = pyaudio.paInt16
        self.device_index = device_index
        self.min_speech_duration = 0.3
        self.silence_threshold = 0.5

        self.vad = webrtcvad.Vad()
        self.vad.set_mode(vad_aggressiveness)

        self.audio_interface = pyaudio.PyAudio()
        self.stream = self.audio_interface.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.frame_size
        )

    def read_frame(self):
        frame = self.stream.read(self.frame_size, exception_on_overflow=False)
        return frame if len(frame) == self.byte_frame_size else None

    def is_speech(self, frame):
        return self.vad.is_speech(frame, self.rate)

    def save_wav(self, filename, frames):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio_interface.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))

    def recognize(self, wav_path):
        with open(wav_path, 'rb') as f:
            audio_data = base64.b64encode(f.read())
        payload = {
            'lang': self.lang,
            'token': '2025@ME@asr',
            'audio': audio_data.decode()
        }
        response = requests.post('http://140.116.245.149:5002/proxy', data=payload, timeout=10)
        return response.json().get('sentence', '') if response.status_code == 200 else ""

    def record_once(self):
        speech_frames = []
        is_speaking = False
        silence_start = None
        speech_start = None

        while True:
            frame = self.read_frame()
            if frame is None:
                continue

            if self.is_speech(frame):
                if not is_speaking:
                    is_speaking = True
                    speech_start = time.time()
                speech_frames.append(frame)
                silence_start = None
            else:
                if is_speaking:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > self.silence_threshold:
                        if speech_frames and (time.time() - speech_start) >= self.min_speech_duration:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            wav_file = f"speech_{timestamp}.wav"
                            try:
                                self.save_wav(wav_file, speech_frames)
                                result = self.recognize(wav_file)
                                os.remove(wav_file)
                                return result
                            except:
                                return ""
                        return ""  # Skip short noise
                else:
                    speech_frames = []

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio_interface.terminate()

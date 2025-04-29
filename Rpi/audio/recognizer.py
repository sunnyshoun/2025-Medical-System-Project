from typing import Optional, List
import requests
import base64
import time
import wave
import os
from datetime import datetime

class StreamingRecognizer:
    def __init__(self, audio_recorder, language="English"):
        self.audio_recorder = audio_recorder
        self.language = language
        self.speech_frames = []
        self.is_speaking = False
        self.silence_start = None
        self.speech_start = None
        self.silence_threshold = 0.5  # Silence duration in seconds
        self.min_speech_duration = 0.3  # Minimum speech duration in seconds
        self.api_url = "http://140.116.245.149:5002/proxy"
        self.max_retries = 3
        self.retry_delay = 1.0  # Seconds
        self.result = None
        self.is_running = False
        self.audio_files_dir = os.path.join(os.path.dirname(__file__), "audioFiles")
        # 確保 audioFiles 資料夾存在
        os.makedirs(self.audio_files_dir, exist_ok=True)

    def start(self) -> None:
        """Start the recognition process in streaming mode."""
        self.result = None
        self.is_running = True
        while self.is_running:
            result = self.recognize_once()
            if result and result != "<{silent}>":
                self.result = result
                break

    def stop(self) -> None:
        """Stop the recognition process."""
        self.is_running = False

    def recognize_once(self) -> Optional[str]:
        """Run speech recognition once and block until result is returned."""
        while True:
            frame = self.audio_recorder.get_frame()
            if frame is None:
                time.sleep(0.01)  # Prevent tight loop
                continue
            
            if self.audio_recorder.is_speech(frame):
                if not self.is_speaking:
                    self.is_speaking = True
                    self.speech_start = time.time()
                self.speech_frames.append(frame)
                self.silence_start = None
            else:
                if self.is_speaking:
                    if self.silence_start is None:
                        self.silence_start = time.time()
                    elif time.time() - self.silence_start > self.silence_threshold:
                        # End of speech segment
                        if self.speech_frames and (time.time() - self.speech_start) >= self.min_speech_duration:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            wav_file = os.path.join(self.audio_files_dir, f"speech_{timestamp}.wav")
                            if self.save_wav(wav_file, self.speech_frames):
                                result = self.recognize(wav_file)
                                try:
                                    os.remove(wav_file)
                                except OSError:
                                    pass
                                if result and result != "<{silent}>":
                                    return result
                        self.speech_frames = []
                        self.is_speaking = False
                        self.silence_start = None
                        self.speech_start = None
                else:
                    self.speech_frames = []  # Clear buffer if no speech

    def recognize(self, wav_path: str) -> Optional[str]:
        """Send WAV file to recognition API and return the result."""
        for attempt in range(self.max_retries):
            try:
                with open(wav_path, 'rb') as f:
                    raw_audio = f.read()
                audio_data = base64.b64encode(raw_audio)
                payload = {
                    'lang': self.language,
                    'token': '2025@ME@asr',
                    'audio': audio_data.decode()
                }
                response = requests.post(self.api_url, data=payload, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    return result.get('sentence', '<{silent}>')
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
            except Exception:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        return "<{silent}>"

    def save_wav(self, filename: str, frames: List[bytes]) -> bool:
        """Save audio frames to a WAV file."""
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.audio_recorder.channels)
                wf.setsampwidth(self.audio_recorder.audio_interface.get_sample_size(self.audio_recorder.format))
                wf.setframerate(self.audio_recorder.rate)
                wf.writeframes(b''.join(frames))
            return True
        except Exception:
            return False
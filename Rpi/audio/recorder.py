from typing import Optional
import pyaudio
import webrtcvad
import wave
import time
import os

class AudioRecorder:
    def __init__(self, device_index: int = 11, rate: int = 16000, frame_duration: int = 30, vad_mode: int = 3):
        self.rate = rate
        self.frame_duration = frame_duration  # ms
        self.frame_size = int(rate * frame_duration / 1000)  # samples
        self.byte_frame_size = self.frame_size * 2  # bytes (16-bit = 2 bytes)
        self.channels = 1
        self.format = pyaudio.paInt16
        self.device_index = device_index
        self.audio_files_dir = os.path.join(os.path.dirname(__file__), "audioFiles")
        try:
            os.makedirs(self.audio_files_dir, exist_ok=True)
        except OSError as e:
            print(f"無法創建 audioFiles 資料夾: {e}")

        # Initialize VAD
        self.vad = webrtcvad.Vad(vad_mode)  # Configurable VAD mode (0-3)

        # Initialize PyAudio
        try:
            self.audio_interface = pyaudio.PyAudio()
            self.stream = self.audio_interface.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.frame_size
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize audio stream: {e}")

    def start(self) -> None:
        try:
            if self.stream is None or not self.stream.is_active():
                if self.stream is not None:
                    self.stream.close()
                if self.audio_interface is None:
                    self.audio_interface = pyaudio.PyAudio()
                self.stream = self.audio_interface.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    input=True,
                    input_device_index=self.device_index,
                    frames_per_buffer=self.frame_size
                )
            self.stream.start_stream()
        except Exception as e:
            print(f"啟動音訊流失敗: {e}")

    def stop(self) -> None:
        try:
            if self.stream is not None:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            if self.audio_interface is not None:
                self.audio_interface.terminate()
                self.audio_interface = None
        except Exception as e:
            print(f"停止音訊流失敗: {e}")

    def get_frame(self) -> Optional[bytes]:
        try:
            if self.stream is None or not self.stream.is_active():
                return None
            frame = self.stream.read(self.frame_size, exception_on_overflow=False)
            if len(frame) != self.byte_frame_size:
                return None
            return frame
        except Exception as e:
            print(f"獲取音訊框架失敗: {e}")
            return None

    def is_speech(self, frame: bytes) -> bool:
        try:
            return self.vad.is_speech(frame, self.rate)
        except Exception:
            return False

    def record_speech(self, max_duration: float = 5.0, silence_threshold: float = 0.5, min_speech_duration: float = 0.3) -> Optional[str]:
        """
        錄製語音片段，當檢測到語音時儲存為 WAV 檔案。
        max_duration 從首次檢測到語音開始計時，直到靜音條件滿足或超過 max_duration。
        回傳 WAV 檔案路徑，若無語音或失敗則回傳 None。
        """
        self.start()
        frames = []
        is_speaking = False
        silence_start = None
        speech_start = None

        while True:
            frame = self.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            if self.is_speech(frame):
                if not is_speaking:
                    is_speaking = True
                    speech_start = time.time()
                frames.append(frame)
                silence_start = None
            else:
                if is_speaking:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > silence_threshold:
                        if frames and (time.time() - speech_start) >= min_speech_duration:
                            wav_file = os.path.join(self.audio_files_dir, "record.wav")
                            try:
                                with wave.open(wav_file, 'wb') as wf:
                                    wf.setnchannels(self.channels)
                                    wf.setsampwidth(self.audio_interface.get_sample_size(self.format))
                                    wf.setframerate(self.rate)
                                    wf.writeframes(b''.join(frames))
                                return wav_file
                            except Exception as e:
                                print(f"儲存 WAV 檔案 {wav_file} 失敗: {e}")
                                return None
                        frames = []
                        is_speaking = False
                        silence_start = None
                        speech_start = None
                else:
                    frames = []

            if is_speaking and speech_start is not None and (time.time() - speech_start) > max_duration:
                if frames and (time.time() - speech_start) >= min_speech_duration:
                    wav_file = os.path.join(self.audio_files_dir, "record.wav")
                    with wave.open(wav_file, 'wb') as wf:
                        wf.setnchannels(self.channels)
                        wf.setsampwidth(self.audio_interface.get_sample_size(self.format))
                        wf.setframerate(self.rate)
                        wf.writeframes(b''.join(frames))
                    return wav_file
                break

        if self.stream is not None:
            self.stream.stop_stream()
        return None
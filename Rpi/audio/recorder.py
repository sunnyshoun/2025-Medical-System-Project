import os
import time
import wave
import pyaudio
import webrtcvad
from typing import Optional
import contextlib
import sys
import ctypes
from config_manager import load_config

@contextlib.contextmanager
def suppress_alsa_errors():
    """Temporarily suppress ALSA (and other C library) stderr output."""
    try:
        # get C stderr
        libc = ctypes.CDLL(None)
        c_stderr = ctypes.c_void_p.in_dll(libc, 'stderr')

        # flush and redirect stderr to /dev/null
        sys.stderr.flush()
        devnull = os.open(os.devnull, os.O_WRONLY)
        saved_stderr_fd = os.dup(2)
        os.dup2(devnull, 2)

        yield

    finally:
        # restore stderr
        os.dup2(saved_stderr_fd, 2)
        os.close(devnull)

class AudioRecorder:
    def __init__(self, rate: int = 16000, frame_duration: int = 30, vad_mode: int = 3):
        config = load_config()
        self.headphone_mac = config.get('HEADPHONE_DEVICE_MAC')
        if not self.headphone_mac:
            raise ValueError("HEADPHONE_DEVICE_MAC not found in config")

        self.rate = rate
        self.frame_duration = frame_duration
        self.frame_size = int(rate * frame_duration / 1000)
        self.byte_frame_size = self.frame_size * 2
        self.audio_dir = os.path.join(os.path.dirname(__file__), "audioFiles")
        os.makedirs(self.audio_dir, exist_ok=True)

        self.vad = webrtcvad.Vad(vad_mode)
        with suppress_alsa_errors():
            self.audio_interface = pyaudio.PyAudio()
            device_index = self.find_bluetooth_device_index()
            self.device_index = device_index
            self.stream = self.audio_interface.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.frame_size
            )

    def find_bluetooth_device_index(self):
        """動態查找藍芽設備的 device_index"""
        for i in range(self.audio_interface.get_device_count()):
            device_info = self.audio_interface.get_device_info_by_index(i)
            if device_info["maxInputChannels"] > 0 and self.headphone_mac.lower() in device_info["name"].lower():
                return i
        raise ValueError(f"No Bluetooth audio input device found for MAC: {self.headphone_mac}")

    def start(self):
        if not self.stream.is_active():
            self.stream.start_stream()

    def stop(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio_interface:
            self.audio_interface.terminate()

    def get_frame(self) -> Optional[bytes]:
        try:
            frame = self.stream.read(self.frame_size, exception_on_overflow=False)
            return frame if len(frame) == self.byte_frame_size else None
        except Exception:
            return None

    def is_speech(self, frame: bytes) -> bool:
        try:
            return self.vad.is_speech(frame, self.rate)
        except Exception:
            return False

    def record_speech(self, max_duration: float = 5.0, silence_threshold: float = 0.5, min_speech_duration: float = 0.3) -> Optional[str]:
        self.start()
        frames, is_speaking, silence_start, speech_start = [], False, None, None
        start_time = time.time()

        while time.time() - start_time < max_duration + 1:
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
            elif is_speaking:
                silence_start = silence_start or time.time()
                if time.time() - silence_start > silence_threshold:
                    break

        if is_speaking and speech_start and (time.time() - speech_start) >= min_speech_duration:
            file_path = os.path.join(self.audio_dir, "record.wav")
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(self.audio_interface.get_sample_size(pyaudio.paInt16))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
            return file_path
        return None
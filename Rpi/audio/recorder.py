from typing import Optional
import pyaudio
import webrtcvad

class AudioRecorder:
    def __init__(self, device_index: int = 11, rate: int = 16000, frame_duration: int = 30, vad_mode: int = 2):
        self.rate = rate
        self.frame_duration = frame_duration  # ms
        self.frame_size = int(rate * frame_duration / 1000)  # samples
        self.byte_frame_size = self.frame_size * 2  # bytes (16-bit = 2 bytes)
        self.channels = 1
        self.format = pyaudio.paInt16
        self.device_index = device_index

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
        self.stream.start_stream()

    def stop(self) -> None:
        try:
            self.stream.stop_stream()
            self.stream.close()
            self.audio_interface.terminate()
        except Exception:
            pass

    def get_frame(self) -> Optional[bytes]:
        try:
            frame = self.stream.read(self.frame_size, exception_on_overflow=False)
            if len(frame) != self.byte_frame_size:
                return None
            return frame
        except Exception:
            return None

    def is_speech(self, frame: bytes) -> bool:
        try:
            return self.vad.is_speech(frame, self.rate)
        except Exception:
            return False
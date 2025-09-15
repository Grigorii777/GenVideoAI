import numpy as np
import torch
import torchaudio
from transformers import pipeline


class TTSService:
    def __init__(self, model: str = "facebook/mms-tts-rus", device: str = "mps"):
        """
        Initialize the TTS pipeline.
        :param model: HuggingFace model name
        :param device: execution device ("cpu" or "mps" for Mac)
        """
        self.synth = pipeline("text-to-speech", model=model, device=device)

    def synthesize(self, text: str, path: str = "output.wav") -> str:
        """
        Generate speech and save it as a WAV file.
        :param text: input text for speech synthesis
        :param path: output file path
        :return: path to the generated audio file
        """
        speech = self.synth(text)

        audio = speech["audio"]

        # Remove extra dimension if shape is (N,1)
        if audio.ndim > 1:
            audio = audio.squeeze()

        # Convert float audio [-1,1] to int16 PCM format
        max_int16 = np.iinfo(np.int16).max
        audio_int16 = (audio * max_int16).astype(np.int16)

        # Convert to torch tensor (channels, samples)
        audio_tensor = torch.from_numpy(audio_int16).unsqueeze(0)

        # Save audio with torchaudio
        torchaudio.save(path, audio_tensor, speech["sampling_rate"], format="wav")

        return path


if __name__ == "__main__":
    tts = TTSService()
    file_path = tts.synthesize("Я тут озвучиваю нормально", "test.wav")
    print(f"File saved: {file_path} ✅")

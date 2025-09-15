import torch
from TTS.api import TTS

# Patch torch.load to force weights_only=False
_orig_load = torch.load
def _patched_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _orig_load(*args, **kwargs)
torch.load = _patched_load

# Init XTTS
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).to("mps")

tts.tts_to_file(
    text="Hi, Grisha! XTTS finally loaded with the weights_only=False patch.",
    speaker_wav="silero_out.wav",
    language="ru",
    file_path="xtts_test.wav"
)

print("File saved: xtts_test.wav ✅")

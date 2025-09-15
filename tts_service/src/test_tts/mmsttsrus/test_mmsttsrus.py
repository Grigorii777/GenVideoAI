import torch
import soundfile as sf
from transformers import VitsModel, AutoTokenizer

# model
model_id = "facebook/mms-tts-rus"

# load
model = VitsModel.from_pretrained(model_id)
tokenizer = AutoTokenizer.from_pretrained(model_id)

device = "mps" if torch.backends.mps.is_available() else "cpu"
model = model.to(device)

text = """The legend of Romulus and Remus sets the tone for Rome's early history. Archaeological
        evidence reminds us the city emerged through the gradual coexistence of Latin settlements.
        Social and political institutions began to take shape here at the crossroads of trade and defense."""

# convert text to tokens
inputs = tokenizer(text, return_tensors="pt").to(device)

# generate audio
with torch.no_grad():
    output = model(**inputs).waveform

# save to wav
sf.write("output.wav", output.squeeze().cpu().numpy(), model.config.sampling_rate)
print("File saved: output.wav")

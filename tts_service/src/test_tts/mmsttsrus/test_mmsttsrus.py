import torch
import soundfile as sf
from transformers import VitsModel, AutoTokenizer

# модель
model_id = "facebook/mms-tts-rus"

# загружаем
model = VitsModel.from_pretrained(model_id)
tokenizer = AutoTokenizer.from_pretrained(model_id)

device = "mps" if torch.backends.mps.is_available() else "cpu"
model = model.to(device)

text = """Легенда о Ромуле и Реме задаёт тон ранней истории Рима. Археологические
        данные напоминают, что город возник в ходе постепенного сосуществования латинских
        поселений. Социальные и политические институты начали формироваться здесь,
        на перекрёстке торговли и обороны."""

# преобразуем текст в токены
inputs = tokenizer(text, return_tensors="pt").to(device)

# генерируем аудио
with torch.no_grad():
    output = model(**inputs).waveform

# сохраняем в wav
sf.write("output.wav", output.squeeze().cpu().numpy(), model.config.sampling_rate)
print("Файл сохранён: output.wav")

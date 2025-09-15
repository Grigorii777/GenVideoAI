from diffusers import StableDiffusionPipeline
import torch

device = "mps"

pipe = StableDiffusionPipeline.from_pretrained(
    "stabilityai/sd-turbo",   # или "runwayml/stable-diffusion-v1-5"
).to(device)

pipe.enable_attention_slicing()
pipe.enable_vae_slicing()

# Заглушка для safety_checker
def dummy_safety_checker(images, clip_input):
    return images, [False] * len(images)

# Заглушка для feature_extractor с поддержкой .to()
class DummyOutput:
    def __init__(self):
        self.pixel_values = torch.zeros(1, 3, 224, 224)
    def to(self, device):
        self.pixel_values = self.pixel_values.to(device)
        return self

class DummyFeatureExtractor:
    def __call__(self, images, return_tensors="pt"):
        return DummyOutput()

pipe.safety_checker = dummy_safety_checker
pipe.feature_extractor = DummyFeatureExtractor()

prompt = "Rome"

image = pipe(prompt, num_inference_steps=1, height=512, width=512).images[0]
image.save("output.png")

print("✅ Сохранено в output.png")

from PIL import Image
import fix_import  # IMPORTANT!!!!
from py_real_esrgan.model import RealESRGAN
import torch
m = RealESRGAN(torch.device("mps" if torch.backends.mps.is_available() else "cpu"), scale=4)
m.load_weights('weights/RealESRGAN_x4.pth', download=True)
m.predict(Image.open("out.png").convert("RGB")).save("upscale.png")

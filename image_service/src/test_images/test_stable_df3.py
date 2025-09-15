# sd_minimal_mps.py
import torch
from diffusers import AutoPipelineForText2Image

# 1) Choose a model: v1.5 / 2.1 / SDXL
model_id = "runwayml/stable-diffusion-v1-5"
# model_id = "stabilityai/stable-diffusion-2-1-base"
# model_id = "stabilityai/stable-diffusion-xl-base-1.0"

device = "mps" if torch.backends.mps.is_available() else "cpu"

# 2) Recommended parameters per model
H, W = 512, 512
STEPS, CFG = 30, 5

prompt = ("Realism, Topic: Warhammer 40,000 The Emperor's Palace. rectilinear, perspective-correct, architectural precision, straight lines, no fisheye, no barrel distortion, tilt-shift lens")

negative_prompt = "high quality"

# 3) Load the pipeline in FP16
pipe = AutoPipelineForText2Image.from_pretrained(
    model_id,
    dtype=torch.float16,
    use_safetensors=True,
    low_cpu_mem_usage=True,
)
pipe.to(device)

# 4) Save VRAM
pipe.enable_attention_slicing()
pipe.vae.enable_slicing()
pipe.vae.enable_tiling()
# If you hit OOM uncomment (slower but more stable):
# pipe.enable_model_cpu_offload()

with torch.inference_mode():
    image = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=STEPS,
        guidance_scale=CFG,
        height=H,
        width=W,
    ).images[0]

image.save("out.png")
if device == "mps":
    torch.mps.empty_cache()

print(f"✅ Saved out.png | model={model_id} {W}x{H}, steps={STEPS}, cfg={CFG}")

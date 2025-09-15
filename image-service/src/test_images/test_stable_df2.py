import torch
from diffusers import AutoPipelineForText2Image

# Optionally, relax the MPS limit (0.6…0.9 possible; 0.0 — no limit, proceed with caution)
# os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"

device = "mps" if torch.backends.mps.is_available() else "cpu"

pipe = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/sd-turbo",
    variant="fp16",
    use_safetensors=True,
    low_cpu_mem_usage=True,
)
pipe.to(device)

# Memory savings
pipe.enable_attention_slicing()
pipe.vae.enable_slicing()
pipe.vae.enable_tiling()
# The most stringent economy (slower, but almost no OOM):
# pipe.enable_model_cpu_offload()

prompt = """Aerial view of a colossal gothic cathedral in the Warhammer 40k universe,
towering black spires, glowing stained glass, smoke and fog drifting over a grimdark city,
epic cinematic scale, dark tones, ultra-detailed
"""

H, W = 512, 512

with torch.inference_mode():
    image = pipe(
        prompt,
        num_inference_steps=1,
        guidance_scale=0.0,
        height=H,
        width=W,
    ).images[0]

image.save("raw.png")
torch.mps.empty_cache()
print("✅ Saved raw.png")

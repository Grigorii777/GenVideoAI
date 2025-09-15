# hf_compat.py — execute DO before importing py_real_esrgan
import sys, huggingface_hub as hf
try:
    from huggingface_hub import cached_download  # старый API?
except Exception:
    from huggingface_hub import hf_hub_download as _cd
    # Export the symbol to make it work: from huggingface_hub import cached_download
    setattr(hf, "cached_download", _cd)
    sys.modules["huggingface_hub"].cached_download = _cd

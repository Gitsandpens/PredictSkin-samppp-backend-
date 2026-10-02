from io import BytesIO
from pathlib import Path
from fastapi import HTTPException
from PIL import Image, ImageOps

EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_BYTES = 10 * 1024 * 1024
BAD_IMAGE = "Unable to read this image. Please upload a valid JPG, JPEG, PNG, or WEBP image."


def load_rgb(source):
    """Open a path or bytes, check it is a real JPEG/PNG/WEBP, return an RGB PIL image."""
    with Image.open(source) as img:
        if img.format not in {"JPEG", "PNG", "WEBP"}:
            raise ValueError("unsupported format")
        img = ImageOps.exif_transpose(img)
        img.load()
        return img.convert("RGB")


def find_first_image(folder: Path):
    """First valid image in a class folder (any file name), or None."""
    if not folder.is_dir():
        return None
    for p in sorted(folder.iterdir()):
        if p.is_file() and p.suffix.lower() in EXTS:
            try:
                load_rgb(p)
                return p
            except Exception:
                continue
    return None


def decode_upload(data: bytes):
    if len(data) > MAX_BYTES:
        raise HTTPException(400, "Image is larger than 10 MB. Please upload a smaller image.")
    try:
        return load_rgb(BytesIO(data))
    except Exception:
        raise HTTPException(400, BAD_IMAGE)

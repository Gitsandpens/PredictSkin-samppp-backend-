"""Fills any empty class folder in backend/dataset from a public Kaggle dataset.

Runs at startup, and only if a class has no image yet (so images you add by hand are never replaced).
The Kaggle dataset can be either one folder per class, or loose files named after the class
(Eczema.webp, normal skin.jpg ...). Matching ignores case, spaces and underscores.
"""
import io, re, shutil, tempfile, urllib.request, zipfile
from pathlib import Path
from utils.image_utils import EXTS, find_first_image


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _download(handle):
    try:
        import kagglehub  # official downloader, works without a token for public datasets
        return kagglehub.dataset_download(handle)
    except Exception:
        pass
    # Fallback: Kaggle's public download URL
    req = urllib.request.Request(f"https://www.kaggle.com/api/v1/datasets/download/{handle}", headers={"User-Agent": "predictskin"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    out = tempfile.mkdtemp(prefix="kaggle_")
    zipfile.ZipFile(io.BytesIO(data)).extractall(out)
    return out


def sync_missing(dataset_dir: Path, classes, handle):
    """Returns None when everything is fine, otherwise a short note explaining what went wrong."""
    needed = [k for k in classes if find_first_image(dataset_dir / k) is None]
    if not needed:
        return None
    try:
        src = Path(_download(handle))
    except Exception as e:
        return f"Could not download Kaggle dataset '{handle}': {e}"
    images = [p for p in src.rglob("*") if p.is_file() and p.suffix.lower() in EXTS]
    for key in needed:
        nk = _norm(key)
        match = (next((p for p in images if _norm(p.stem) == nk or _norm(p.parent.name) == nk), None)
                 or next((p for p in images if nk in _norm(p.stem)), None))
        if match:
            (dataset_dir / key).mkdir(parents=True, exist_ok=True)
            shutil.copy2(match, dataset_dir / key / match.name)
    still = [k for k in needed if find_first_image(dataset_dir / k) is None]
    return f"Kaggle dataset '{handle}' has no image for: {', '.join(still)}." if still else None

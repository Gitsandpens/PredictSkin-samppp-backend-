"""Reference-image comparison: cosine similarity between embeddings.

Score transformation (documented for the report):
  1. cosine_i = dot(upload_embedding, reference_embedding_i)   (both L2-normalised)
  2. match_score_i = softmax(cosine_i / TEMPERATURE) over the 7 classes
So match scores sum to 100%. The raw cosine values are returned too ("raw_cosine").
Nothing is random or hard-coded.
"""
import os
from pathlib import Path
import numpy as np
from model.feature_extractor import FeatureExtractor
from utils.image_utils import find_first_image, load_rgb
from utils.kaggle_sync import sync_missing

DATASET_DIR = Path(__file__).resolve().parent.parent / "dataset"
CLASSES = {  # folder name -> display name
    "normal_skin": "Normal Skin", "eczema": "Eczema", "psoriasis": "Psoriasis",
    "ringworm": "Ringworm", "chickenpox": "Chickenpox", "rosacea": "Rosacea",
    "cellulitis": "Cellulitis",
}
# Configurable thresholds (environment variables).
TEMPERATURE = float(os.getenv("SOFTMAX_TEMPERATURE", "0.05"))
MIN_COSINE = float(os.getenv("MIN_COSINE", "0.55"))   # best raw cosine below this -> uncertain
KAGGLE_DATASET = os.getenv("KAGGLE_DATASET", "sheetalkaggle99/10skin")  # set empty to disable
MIN_MARGIN = float(os.getenv("MIN_MARGIN", "0.03"))   # best minus second-best cosine below this -> uncertain


class ReferenceStore:
    def __init__(self):
        self.extractor = None
        self.paths, self.embeddings = {}, {}
        self.missing = list(CLASSES)
        self.error = None
        self.sync_note = None

    @property
    def ready(self):
        return not self.missing and self.error is None and len(self.embeddings) == len(CLASSES)

    def load(self):
        """Scan folders, embed each reference image once, keep embeddings in memory."""
        self.paths, self.embeddings, self.error = {}, {}, None
        if KAGGLE_DATASET:
            self.sync_note = sync_missing(DATASET_DIR, list(CLASSES), KAGGLE_DATASET)
        for key in CLASSES:
            p = find_first_image(DATASET_DIR / key)
            if p:
                self.paths[key] = p
        self.missing = [k for k in CLASSES if k not in self.paths]
        try:
            if self.extractor is None:
                self.extractor = FeatureExtractor()
            for key, p in self.paths.items():
                self.embeddings[key] = self.extractor.embed(load_rgb(p))
        except Exception as e:  # e.g. pretrained weights could not be downloaded
            self.error = f"Model could not be loaded: {e}"

    def status(self):
        return {
            "classes": {label: key in self.paths for key, label in CLASSES.items()},
            "missing": [CLASSES[k] for k in self.missing],
            "ready": self.ready,
            "error": self.error,
            "note": self.sync_note,
            "model": getattr(self.extractor, "name", None),
        }

    def predict(self, img):
        keys = list(CLASSES)
        q = self.extractor.embed(img)
        cos = np.array([float(np.dot(q, self.embeddings[k])) for k in keys])
        z = cos / TEMPERATURE
        p = np.exp(z - z.max())
        p /= p.sum()
        order = np.argsort(-cos)
        top, second = int(order[0]), int(order[1])
        margin = float(cos[top] - cos[second])
        uncertain = bool(cos[top] < MIN_COSINE or margin < MIN_MARGIN)
        labels = [CLASSES[k] for k in keys]
        return {
            "prediction": labels[top],
            "match_score": float(p[top]),
            "cosine": float(cos[top]),
            "margin": margin,
            "uncertain": uncertain,
            "scores": {labels[i]: float(p[i]) for i in range(len(keys))},
            "raw_cosine": {labels[i]: float(cos[i]) for i in range(len(keys))},
            "ranking": [labels[int(i)] for i in order],
            "thresholds": {"min_cosine": MIN_COSINE, "min_margin": MIN_MARGIN, "temperature": TEMPERATURE},
        }

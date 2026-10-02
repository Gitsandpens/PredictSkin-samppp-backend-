"""Pretrained CNN used as a feature extractor (final classification layer removed)."""
import os
import numpy as np
import torch
from torchvision import models, transforms


class FeatureExtractor:
    def __init__(self, name=None):
        name = (name or os.getenv("MODEL_NAME", "mobilenet_v2")).lower()
        if name == "resnet50":
            model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            model.fc = torch.nn.Identity()  # 2048-d embedding
        else:
            model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
            model.classifier = torch.nn.Identity()  # 1280-d embedding
            name = "mobilenet_v2"
        self.name = name
        self.model = model.eval()
        # Standard ImageNet preprocessing expected by these pretrained weights.
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    @torch.no_grad()
    def embed(self, img):
        """PIL RGB image -> L2-normalised embedding (so a dot product is cosine similarity)."""
        x = self.transform(img).unsqueeze(0)
        v = self.model(x).squeeze(0).numpy().astype(np.float64)
        return v / (np.linalg.norm(v) + 1e-12)

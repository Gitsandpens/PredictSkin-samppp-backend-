import shutil
from pathlib import Path
import kagglehub

path = kagglehub.dataset_download("sheetalkaggle99/10skin")
target = Path(__file__).parent / "dataset"
shutil.copytree(path, target, dirs_exist_ok=True)
print("Data yahan aa gaya:", target)
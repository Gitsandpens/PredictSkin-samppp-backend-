"""Checks that each reference image ranks its own class first. Run from the backend folder."""
import sys
from model.similarity import CLASSES, ReferenceStore
from utils.image_utils import load_rgb

store = ReferenceStore()
store.load()
print("Dataset status:", store.status())
if not store.ready:
    sys.exit("Dataset not ready - fix the problem above first.")
failed = False
for key, path in store.paths.items():
    r = store.predict(load_rgb(path))
    ok = r["prediction"] == CLASSES[key]
    failed |= not ok
    print(f"{'PASS' if ok else 'FAIL'}  {path.name:<22} -> {r['prediction']} ({r['match_score']:.1%}, cosine {r['cosine']:.4f})")
sys.exit(1 if failed else 0)

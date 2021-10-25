import zipfile
from pathlib import Path
import os

ROOT = '.'
PY_FILE = 'A2.py'

p = Path(ROOT).resolve()
for sub in p.glob('*.zip'):
    print(f"Checking {sub.name}")
    sub_name = sub.stem # We expect the zip file name to be same as the folder name
    with zipfile.ZipFile(sub, 'r') as zip_ref:
        zip_ref.extractall(ROOT)
    if not(sub_name[:2] == "A2" and "-" in sub_name):
        print("Error: Zip folder name incorrect. Please use correct format A2-<Entry No.1>-<Entry No.2>")
    else:
        sub_eval_dir = p / sub_name
        if not os.path.exists(sub_eval_dir):
            print("Error: Unzipped folder and zip have different names")
        elif not os.path.exists(sub_eval_dir / PY_FILE):
            print("Error: No A2.py found!")
        else:
            print("Correct Format!")
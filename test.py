import os
from datetime import date

SAMPLE_NAME = "test_sample"

current_dir = os.getcwd()
today = date.today()
directory = f"[{today}] {SAMPLE_NAME}"
path = os.path.join(current_dir, directory)
os.mkdir(path)
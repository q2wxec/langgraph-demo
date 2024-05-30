import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print(BASE_DIR)
def load_prompt(path):
    path =os.path.join(BASE_DIR,path)
    with open( path, 'r', encoding='utf-8') as f:
        return f.read()
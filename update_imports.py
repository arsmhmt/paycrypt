import os
import re
from pathlib import Path

def update_imports_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace 'from app import db' with 'from app.extensions.extensions import db'
    content = re.sub(
        r'^from app import db\b',
        'from app.extensions.extensions import db',
        content,
        flags=re.MULTILINE
    )
    
    # Replace 'from app import mail' with 'from app.extensions.extensions import mail'
    content = re.sub(
        r'^from app import mail\b',
        'from app.extensions.extensions import mail',
        content,
        flags=re.MULTILINE
    )
    
    # Replace 'from app import db, mail' with 'from app.extensions.extensions import db, mail'
    content = re.sub(
        r'^from app import (db, mail|mail, db)\b',
        'from app.extensions.extensions import db, mail',
        content,
        flags=re.MULTILINE
    )
    
    # Replace 'from app import app' with 'from app import create_app'
    content = re.sub(
        r'^from app import app\b',
        'from app import create_app',
        content,
        flags=re.MULTILINE
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    # Get all Python files in the app directory
    app_dir = Path('app')
    python_files = list(app_dir.glob('**/*.py'))
    
    for file_path in python_files:
        update_imports_in_file(file_path)
        print(f"Updated imports in {file_path}")

if __name__ == '__main__':
    main()

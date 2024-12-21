import os
import subprocess
import tempfile
import json
from datetime import datetime

def push_content_to_repo(image_filename, target_image_dir, image_outputs, git_repo_url, branch, username, email, target_dir, filename, content, target_article_json_path, title, description, keywords):
    """
    Clones the repo, creates/updates the target directory, writes the file,
    and pushes the changes.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone the repo
        subprocess.run(["git", "clone", git_repo_url, tmpdir], check=True)
        
        original_dir = os.getcwd()

        os.chdir(tmpdir)
        
        # Checkout the target branch
        subprocess.run(["git", "checkout", branch], check=True)
        
        # Set user config
        subprocess.run(["git", "config", "user.name", username], check=True)
        subprocess.run(["git", "config", "user.email", email], check=True)
        
        # Ensure target_dir exists
        target_path = os.path.join(tmpdir, target_dir)
        os.makedirs(target_path, exist_ok=True)
        

        # Ensure the output directory exists
        os.makedirs(target_image_dir, exist_ok=True)

        # Save the image
        image_path = os.path.join(target_image_dir, image_filename)

        print(f"Saving image to {image_path}")

        with open(image_path, "wb") as f:
            f.write(image_outputs[0].read())

        # Write file
        file_path = os.path.join(target_path, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        date_str = datetime.utcnow().isoformat() + "Z"

        target_article_json_path = os.path.join(tmpdir, target_article_json_path)
        # modify the article json:
        if len(target_article_json_path) > 0:
            with open(target_article_json_path, 'r', encoding='utf-8') as f:
                article_json = json.load(f)
                new_article_json = {
                    "title": title,
                    "description": description,
                    "date": date_str,
                    "lastModified": date_str,
                    "path": os.path.join(target_dir, filename)
                }

                article_json.append(new_article_json)

            with open(target_article_json_path, 'w', encoding='utf-8') as f:
                json.dump(article_json, f, indent=4)

        # Git add, commit, push
        subprocess.run(["git", "add", file_path], check=True)
        subprocess.run(["git", "add", image_path], check=True)
        subprocess.run(["git", "add", target_article_json_path], check=True)
        subprocess.run(["git", "commit", "-m", f"Add article: {filename}"], check=True)
        subprocess.run(["git", "push", "origin", branch], check=True)
        
        os.chdir(original_dir)

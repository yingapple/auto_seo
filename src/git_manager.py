import os
import subprocess
import tempfile

def push_content_to_repo(git_repo_url, branch, username, email, target_dir, filename, content):
    """
    Clones the repo, creates/updates the target directory, writes the file,
    and pushes the changes.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone the repo
        subprocess.run(["git", "clone", git_repo_url, tmpdir], check=True)
        
        os.chdir(tmpdir)
        
        # Checkout the target branch
        subprocess.run(["git", "checkout", branch], check=True)
        
        # Set user config
        subprocess.run(["git", "config", "user.name", username], check=True)
        subprocess.run(["git", "config", "user.email", email], check=True)
        
        # Ensure target_dir exists
        target_path = os.path.join(tmpdir, target_dir)
        os.makedirs(target_path, exist_ok=True)
        
        # Write file
        file_path = os.path.join(target_path, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Git add, commit, push
        subprocess.run(["git", "add", file_path], check=True)
        subprocess.run(["git", "commit", "-m", f"Add article: {filename}"], check=True)
        subprocess.run(["git", "push", "origin", branch], check=True)

import os

def load_env():
    # Simple .env loader
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#'):
                    key, val = line.strip().split('=', 1)
                    os.environ[key.strip()] = val.strip()

def get_config():
    load_env()
    config = {
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', ''),
        'REPLICATE_API_TOKEN': os.environ.get('REPLICATE_API_TOKEN', ''),
        'GIT_REPO_URL': os.environ.get('GIT_REPO_URL', ''),
        'GIT_BRANCH': os.environ.get('GIT_BRANCH', 'main'),
        'GIT_USERNAME': os.environ.get('GIT_USERNAME', 'User'),
        'GIT_EMAIL': os.environ.get('GIT_EMAIL', 'user@example.com'),
        'TARGET_CONTENT_DIR': os.environ.get('TARGET_CONTENT_DIR', 'content'),
        'IMAGE_OUTPUT_DIR': os.environ.get('IMAGE_OUTPUT_DIR', 'public/images/generated'),
        'TOPIC_PROMPT': os.environ.get('TOPIC_PROMPT', 'Tech industry insights'),
        'OPENAI_API_BASE_URL': os.environ.get('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
    }
    return config

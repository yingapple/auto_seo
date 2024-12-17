# My SEO Automation Tool

This tool automatically:
1. Uses OpenAI's ChatCompletion API (with a gpt-4o-mini model as requested) to select a trending topic and generate a markdown article about it.
2. Pushes the generated `.md` file (with YAML front matter) to a specified Git repository and directory.

## Features

- Fully automated: No need to manually specify topics or titles daily.
- Uses environment variables for configuration.
- Minimal dependencies (only `openai` and `git`).
- Suitable for running daily via cron jobs.

## Requirements

- Python 3.9+ recommended
- `openai` Python package
- A valid OpenAI API key
- `git` installed and accessible via `PATH`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/auto_seo.git
   ```

2. Install dependencies:
   ```bash
   cd auto_seo
   pip install -r requirements.txt
   ```

3. Copy .env.example to .env and fill in the required values:
```bash
cp .env.example .env
```

4. Run the script:
```bash
python src/main.py
```

## Configuration

All configuration is done through the .env file.
- TOPIC_PROMPT: A general theme or instruction. For example, if you set TOPIC_PROMPT=Tech industry insights, the system will ask the model for a trending tech topic each run and write an article about it.
- OPENAI_API_KEY: Your OpenAI API key.
- GIT_REPO_URL: The Git repository URL (SSH or HTTPS).
- GIT_BRANCH: The target branch to push.
- GIT_USERNAME and GIT_EMAIL: Commit user info.
- TARGET_CONTENT_DIR: Directory in the repo where articles will be placed.

## Running Daily

Use a cron job or similar scheduler to run python src/main.py daily. Each run will produce a new, thematically relevant article and push it to the repository.

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

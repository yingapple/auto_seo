import os
from config import get_config
from content_generator import generate_topic_and_metadata, generate_article, load_past_keywords, \
    generate_keywords, fetch_trending_queries, verify_and_refine_keywords, save_past_keywords
from image_generator import generate_image
from git_manager import push_content_to_repo
from datetime import datetime

def main():
    cfg = get_config()

    # Step 0: Load past keywords
    past_kw_data = load_past_keywords()
    past_all_kw = []
    if past_kw_data:
        for cat in past_kw_data:
            past_all_kw.extend(past_kw_data[cat])


    # Step 1: Generate new keywords
    trending = fetch_trending_queries(cfg['TOPIC_PROMPT'])
    external_data = {"trending_queries": trending}

    new_keywords = generate_keywords(cfg['TOPIC_PROMPT'], past_keywords=past_all_kw, external_data=external_data, diversity_factor=0.3)
    refined_keywords = verify_and_refine_keywords(new_keywords)

    # Step 2: Generate topic, title, description, and date
    topic, title, description = generate_topic_and_metadata(refined_keywords, cfg['TOPIC_PROMPT'])
    
    # Step 3: Generate the article content and image prompt
    article_content, image_prompt = generate_article(title, description, refined_keywords, external_data=external_data)
    
    # Step 4: Generate an image using the Replicate API
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    image_filename = f"{timestamp}.webp"
    
    image_outputs = generate_image(
        replicate_api_token=cfg['REPLICATE_API_TOKEN'],
        prompt=image_prompt,
        output_dir=cfg['IMAGE_OUTPUT_DIR'],
        filename=image_filename
    )
    
    # Update the Markdown content to include the image reference
    image_relative_path = cfg['IMAGE_OUTPUT_DIR'] + "/" + image_filename
    
    # remove /public, just for specific github pages
    image_relative_path = image_relative_path.replace("/public", "")
    
    article_content += f"\n\n![Generated Image](/{image_relative_path})"
    
    # Step 5: Push the article and image to the Git repository
    markdown_filename = f"{timestamp}.md"
    push_content_to_repo(
        image_filename=image_filename,
        target_image_dir=cfg['IMAGE_OUTPUT_DIR'],
        image_outputs=image_outputs,
        git_repo_url=cfg['GIT_REPO_URL'],
        branch=cfg['GIT_BRANCH'],
        username=cfg['GIT_USERNAME'],
        email=cfg['GIT_EMAIL'],
        target_dir=cfg['TARGET_CONTENT_DIR'],
        filename=markdown_filename,
        content=article_content,
        target_article_json_path=cfg['TARGET_ARTICLE_JSON_PATH'],
        description=description,
        title=title,
        keywords=refined_keywords
    )
    
    print(f"Article '{title}' and image '{image_filename}' pushed to {cfg['GIT_REPO_URL']}")

    save_past_keywords(refined_keywords)

if __name__ == "__main__":
    main()

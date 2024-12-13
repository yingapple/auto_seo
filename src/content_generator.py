import openai
import json
from datetime import datetime
from pytrends.request import TrendReq

# Get OpenAI API key from config
from config import get_config
cfg = get_config()
openai.api_key = cfg['OPENAI_API_KEY']

def load_past_keywords(path="past_keywords.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_past_keywords(keywords, path="past_keywords.json"):
    with open(path, "w") as f:
        json.dump(keywords, f, indent=2)

def fetch_trending_queries(theme):
    """
    Use pytrends to get trending search queries related to the theme from the past 7 days.
    """
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([theme], cat=0, timeframe='now 7-d', geo='', gprop='')
    related_queries = pytrends.related_queries()
    top_df = related_queries.get(theme, {}).get('top', None)
    if top_df is not None:
        top_queries = top_df['query'].tolist()
        return top_queries[:5] 
    return []

def generate_keywords(theme, past_keywords=None, external_data=None, diversity_factor=0.3):
    """
    Generate a diverse set of keywords from theme and multi-source external data.
    external_data can include:
    {
        "trending_queries": ["query1", "query2", ...],
        "industry_news": ["headline1", "headline2", ...],
        "domain_terms": ["term1", "term2", ...]
    }
    """
    if past_keywords is None:
        past_keywords = []
    if external_data is None:
        external_data = {}

    trending = external_data.get("trending_queries", [])
    news = external_data.get("industry_news", [])
    domain_terms = external_data.get("domain_terms", [])

    current_date = datetime.utcnow().strftime("%Y-%m-%d")

    # 将外部数据整合到提示中
    aux_info = f"""
Date: {current_date}
Theme: "{theme}"
Past Keywords: {past_keywords if past_keywords else "None"}
Diversity Factor: {diversity_factor}

External Data Sources:
- Trending Queries: {trending if trending else "None"}
- Industry News: {news if news else "None"}
- Domain Terms: {domain_terms if domain_terms else "None"}

Instructions:
1. Generate a set of SEO-friendly keywords:
   - ≥5 core keywords (broad, directly related)
   - ≥5 long-tail keywords (reflect user search intent)
   - ≥5 LSI/related semantic keywords
2. Incorporate insights from trending queries and industry news when relevant.
3. Include domain-specific terms if they align with the theme.
4. Ensure about {int(diversity_factor*100)}% new or varied keywords compared to past usage.
5. Return JSON with keys: "core_keywords", "long_tail_keywords", "lsi_keywords".
    """

    messages = [
        {"role": "system", "content": "You are an experienced SEO analyst integrating multiple data sources."},
        {"role": "user", "content": aux_info}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=1200
    )
    
    content = response.choices[0].message.content.strip()
    data = json.loads(content)
    return data

def verify_and_refine_keywords(keywords):
    """
    Use model to verify and refine keyword lists:
    1. Remove irrelevant or valueless keywords
    2. Ensure at least 3 keywords remain in each category
    """
    messages = [
        {"role": "system", "content": "You are an SEO specialist verifying the quality of keywords."},
        {"role": "user", "content": f"""
Given these keywords:
Core: {keywords["core_keywords"]}
Long-tail: {keywords["long_tail_keywords"]}
LSI: {keywords["lsi_keywords"]}

1. Remove irrelevant or low-value keywords.
2. Ensure each category retains at least 3 terms.
3. Return refined lists in JSON.
        """}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.5,
        max_tokens=800
    )

    refined = json.loads(response.choices[0].message.content.strip())
    return refined

def generate_topic_and_metadata(keywords, theme):
    """
    Use refined keywords and theme to generate SEO-optimized metadata:
    - Title includes core keywords
    - Description includes long-tail keywords
    - Returns topic, title, description in JSON format
    """
    messages = [
        {"role": "system", "content": "You are a content strategist specialized in SEO."},
        {"role": "user", "content": f"""
Theme: "{theme}"
Core Keywords: {keywords["core_keywords"]}
Long-tail Keywords: {keywords["long_tail_keywords"]}
LSI Keywords: {keywords["lsi_keywords"]}

Please suggest:
- A trending topic closely aligned with the theme
- A catchy SEO-friendly title including at least one core keyword
- A 1-2 sentence description including at least one long-tail keyword

Return JSON: {{ "topic": "...", "title": "...", "description": "..." }}
        """}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=300
    )

    data = json.loads(response.choices[0].message.content.strip())
    return data["topic"], data["title"], data["description"]

def generate_article(title, description, keywords, external_data=None):
    """
    Create article using title, description, keywords and external data.
    - YAML Front Matter includes title, description, date, keywords
    - Uses H1, H2, H3 structure
    - Integrates keywords and external data (like industry trends, news)
    - Includes external authority links and CTA
    - Adds "Image prompt: ..."
    """
    
    date_str = datetime.utcnow().isoformat() + "Z"
    all_keywords = keywords["core_keywords"] + keywords["long_tail_keywords"] + keywords["lsi_keywords"]
    keyword_list_str = ", ".join(all_keywords)

    trending = external_data.get("trending_queries", []) if external_data else []
    news = external_data.get("industry_news", []) if external_data else []
    domain_terms = external_data.get("domain_terms", []) if external_data else []

    aux_context = f"""
External Data:
- Trending Queries: {trending if trending else "None"}
- Industry News: {news if news else "None"}
- Domain Terms: {domain_terms if domain_terms else "None"}

Incorporate relevant external insights if they add value and context.
"""

    messages = [
        {"role": "system", "content": "You are an expert SEO copywriter following E-E-A-T principles."},
        {"role": "user", "content": f"""
Write a markdown article about: "{title}"

---
title: "{title}"
description: "{description}"
date: "{date_str}"
keywords: [{keyword_list_str}]
---

Requirements:
- Start with # {title} (H1)
- Use H2 and H3 headings for logical structure
- Naturally use core, long-tail, and LSI keywords
- Include at least one authoritative external link
- Add a short CTA at the end
- Use short paragraphs, bullet/numbered lists if helpful
- At the end, add: "Image prompt: ..." describing a relevant image
- Integrate any valuable insights from the external data for increased relevance

{aux_context}
        """}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=2500
    )

    article_content = response.choices[0].message.content.strip()

    # 提取Image Prompt
    lines = article_content.split("\n")
    image_prompt_line = [line for line in lines if line.lower().startswith("image prompt:")]
    image_prompt = image_prompt_line[0].split(":", 1)[1].strip() if image_prompt_line else ""

    return article_content, image_prompt


# ========== Main Process Example (Single Execution) ==========
if __name__ == "__main__":
    # Assuming externally provided theme
    theme = "Sustainable Technology Innovations"

    # Load keywords from past records
    past_kw_data = load_past_keywords()
    past_all_kw = []
    if past_kw_data:
        for cat in past_kw_data:
            past_all_kw.extend(past_kw_data[cat])

    # external data sources (in practice, could be from API or database)
    trending = fetch_trending_queries(theme)
    external_data = {"trending_queries": trending}

    # 1. Generate new keywords (referencing past keywords and external data)
    new_keywords = generate_keywords(theme, past_keywords=past_all_kw, external_data=external_data, diversity_factor=0.3)

    # 2. Verify and refine keywords
    refined_keywords = verify_and_refine_keywords(new_keywords)

    # 3. Generate topic, title, description based on keywords and theme
    topic, title, description = generate_topic_and_metadata(refined_keywords, theme)

    # 4. Generate final article (referencing external data)
    article_content, image_prompt = generate_article(title, description, refined_keywords, external_data=external_data)

    # Output results
    print("==== Refined Keywords ====")
    print(json.dumps(refined_keywords, indent=2))
    print("\n==== Topic, Title, Description ====")
    print("Topic:", topic)
    print("Title:", title)
    print("Description:", description)
    print("\n==== Article Content ====")
    print(article_content)
    print("\nImage Prompt:", image_prompt)

    # Update past keywords archive (for future reference)
    save_past_keywords(refined_keywords)

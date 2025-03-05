import json
import logging
import re
import time
import ast
from openai import OpenAI  

# AI Model Configuration
AI_MODEL = "deepseek-r1-distill-qwen-7b"
AI_SERVER_URL = "http://127.0.0.1:1234/v1"
API_KEY = "lm-studio"

# Configure logging
logging.basicConfig(level=logging.INFO)

def strip_ai_thoughts(text):
    """Removes AI self-reflection or unnecessary text before JSON."""
    logging.info(f"Raw AI Response Before Cleaning: {text}")

    # Remove AI's "<think>...</think>" explanations if they appear
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    # Extract valid JSON inside ```json ... ``` block
    json_match = re.search(r"```json\s*([\s\S]+?)\s*```", text)
    if json_match:
        return json_match.group(1).strip()

    return text.strip()

def extract_json(text):
    """Extracts JSON safely and handles malformed AI responses."""
    text = strip_ai_thoughts(text)

    try:
        return json.loads(text)  # Load as JSON
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(text)  # Try parsing as a Python dict if malformed
        except (SyntaxError, ValueError):
            logging.error("Extracted JSON is invalid.")
    
    logging.error("No valid JSON found in response.")
    return None

def query_ai(prompt, stack, max_retries=3):
    """Queries AI for a script and ensures a valid JSON response."""
    client = OpenAI(base_url=AI_SERVER_URL, api_key=API_KEY)

    system_prompt = (
        "**STRICT FORMAT: RETURN ONLY JSON. DO NOT THINK OR EXPLAIN.**\n"
        "```json\n"
        "{\n"
        "  \"files\": [\n"
        "    {\"name\": \"script.ext\", \"content\": \"# Script content here\"}\n"
        "  ]\n"
        "}\n"
        "```\n"
        "**FAIL IF RESPONSE CONTAINS ANYTHING ELSE.**"
    )

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Generate a minimal {stack} script for '{prompt}'. "
                                   "Only return JSON inside ```json ... ``` format. "
                                   "**STRICTLY NO HTML. STRICTLY NO EXPLANATION.**"
                    },
                ],
                max_tokens=500,
                temperature=0,  # Makes AI follow instructions strictly
                top_p=0,  # Removes variability in responses
            )

            ai_content = response.choices[0].message.content.strip()
            logging.info(f"Raw AI Response: {ai_content}")

            parsed_response = extract_json(ai_content)

            # Ensure it has "files" in the response
            if parsed_response and "files" in parsed_response:
                return parsed_response

            logging.error("Invalid AI response structure. Retrying...")
        
        except Exception as e:
            logging.error(f"AI Request Failed: {str(e)}")

        time.sleep(2)  # Retry delay

    return {"error": "AI failed to generate a valid response.", "files": []}

import json
import re
import httpx
from typing import Dict, Any, List

class ReadmeParser:
    def __init__(self):
        # We assume Ollama is running locally on port 11434
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3.2:latest"

    async def parse_readme(self, readme_text: str) -> Dict[str, Any]:
        # Default fallback
        default_result = {
            "project_name": "",
            "description": "",
            "features": []
        }

        if not readme_text:
            return default_result

        # Construct Prompt for Llama 3.2
        # Llama 3 uses specific prompt templates but usually handles plain instructions well.
        # We will strictly ask for JSON.
        prompt = f"""You are an advanced data extraction agent.
I will provide you with the text of a software project README file.
Your job is to extract the following information into a valid JSON object:
1. "project_name": The name of the project.
2. "description": A concise summary of what the project does (2-3 sentences).
3. "features": A list of key features (array of strings).

README CONTENT:
{readme_text[:4000]}

INSTRUCTIONS:
- You must return ONLY the raw JSON object.
- Do not add "Here is the JSON" or any markdown formatting like ```json ... ```.
- If a field cannot be found, populate it with an empty string or empty list.
"""

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json"  # Ollama supports JSON mode which forces valid JSON output
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.ollama_url, json=payload, timeout=60.0)
                
                if response.status_code != 200:
                    print(f"Ollama Error: {response.status_code} - {response.text}")
                    return default_result
                
                result_data = response.json()
                generated_text = result_data.get("response", "")
                
                return self._extract_json(generated_text)

        except Exception as e:
            print(f"Error during Ollama parsing: {e}")
            return default_result

    def _extract_json(self, text: str) -> Dict[str, Any]:
        try:
            # Find JSON/Dict pattern
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                json_str = match.group(0)
                data = json.loads(json_str)
                
                # Validation types
                return {
                    "project_name": str(data.get("project_name", "")),
                    "description": str(data.get("description", "")),
                    "features": [str(f) for f in data.get("features", []) if isinstance(f, str)]
                }
        except Exception:
            pass
            
        return {
            "project_name": "",
            "description": "",
            "features": []
        }

# Singleton instance
parser = ReadmeParser()

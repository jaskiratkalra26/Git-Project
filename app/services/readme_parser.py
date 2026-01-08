"""
README Parser Service

This module provides functionality to parse README files using an AI model (Ollama).
It extracts structured information such as project name, description, and features
from unstructured text content.
"""

import json
import re
import httpx
from typing import Dict, Any, List, Optional
from app.core.config import OLLAMA_API_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT

class ReadmeParser:
    """
    A service class mainly responsible for parsing README contents using a local LLM via Ollama.
    """
    
    def __init__(self):
        """
        Initializes the ReadmeParser with configuration from app settings.
        """
        # We assume Ollama is running locally on port 11434, configured via environment variables
        self.ollama_url = OLLAMA_API_URL
        self.model_name = OLLAMA_MODEL
        self.timeout = OLLAMA_TIMEOUT

    async def parse_readme(self, readme_text: str) -> Dict[str, Any]:
        """
        Parses the text content of a README file to extract structured project data.

        Args:
            readme_text (str): The raw text content of the README file.

        Returns:
            Dict[str, Any]: A dictionary containing 'project_name', 'description', 
                            and 'features' (list). if parsing fails, returns default empty structures.
        """

        # Default fallback structure in case of errors
        default_result = {
            "project_name": "",
            "description": "",
            "features": []
        }

        if not readme_text:
            return default_result

        # Construct Prompt for Llama 3.2 or compatible model
        # The prompt strictly requests a JSON response to facilitate parsing.
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
                # Increased timeout to handle potentially slow local inference on consumer hardware
                response = await client.post(self.ollama_url, json=payload, timeout=self.timeout)
                
                if response.status_code != 200:
                    # Log error details for debugging (in a real app, use a logger)
                    print(f"Ollama Error: {response.status_code} - {response.text}")
                    return default_result
                
                result_data = response.json()
                generated_text = result_data.get("response", "")
                
                # Debug print to verify model output during development
                print(f"DEBUG: Ollama Raw Output: {generated_text[:100]}...")

                return self._extract_json(generated_text)

        except Exception as e:
            # Catch-all for network errors or model failures to prevent app crash
            print(f"Error during Ollama parsing: {type(e).__name__} - {str(e)}")
            return default_result

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Helper method to extract and validate JSON from the model's textual response.

        Args:
            text (str): The raw string output from the LLM.

        Returns:
            Dict[str, Any]: The validated data dictionary.
        """
        try:
            # Find JSON/Dict pattern in case the model returns extra text despite instructions
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                json_str = match.group(0)
                data = json.loads(json_str)
                
                # Validation and type cleaning to ensure response matches schema
                return {
                    "project_name": str(data.get("project_name", "")),
                    "description": str(data.get("description", "")),
                    "features": [str(f) for f in data.get("features", []) if isinstance(f, str)]
                }
        except Exception:
            # Silent failure on JSON parse error, relying on default return
            pass
            
        return {
            "project_name": "",
            "description": "",
            "features": []
        }

# Singleton instance for import usage
parser = ReadmeParser()

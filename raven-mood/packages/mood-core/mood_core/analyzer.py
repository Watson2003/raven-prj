import collections
from typing import List, Dict
import re

def process_file_content(file_name: str, content: str, client, model: str = "claude-3-5-sonnet-20240620") -> Dict[str, str]:
    """Analyse a single file content and return the mood."""
    lines = content.splitlines()
    if len(lines) > 500:
        return {
            "name": file_name,
            "mood": "CHAOTIC",
            "reason": "File exceeds 500 lines",
            "lines": len(lines)
        }
        
    if getattr(client, "api_key", None) == "your_anthropic_api_key_here":
        num_lines = len(lines)
        if num_lines < 100:
            mood = "CLEAN"
            reason = f"File is short and concise ({num_lines} lines)."
        elif num_lines <= 300:
            mood = "MESSY"
            reason = f"File is getting a bit long ({num_lines} lines)."
        else:
            mood = "CHAOTIC"
            reason = f"File is too large and hard to manage ({num_lines} lines)."
            
        return {
            "name": file_name,
            "mood": mood,
            "reason": reason,
            "lines": num_lines
        }

    
    ext = file_name.split('.')[-1]
    
    user_message = (
        f"Read this code and rate its mood as one of: CLEAN 😊, MESSY 😤, or CHAOTIC 🤯. "
        f"Give one single line reason why.\n\n```{ext}\n{content}\n```"
    )
    
    response = client.messages.create(
        model=model,
        max_tokens=500,
        temperature=0,
        messages=[{"role": "user", "content": user_message}],
    )
    
    # Collect raw response text from Anthropic API
    if hasattr(response.content, "__iter__") and not isinstance(response.content, str):
        # Concatenate all text parts
        raw = "".join(part.text if hasattr(part, "text") else part.get("text", "") for part in response.content)
    else:
        raw = str(response.content)

    # Extract mood keyword (CLEAN, MESSY, CHAOTIC) case‑insensitively
    mood_match = re.search(r"\b(CLEAN|MESSY|CHAOTIC)\b", raw, re.IGNORECASE)
    mood_part = mood_match.group(1).upper() if mood_match else "UNKNOWN"
    # The reason is the rest of the response after the mood keyword
    reason_part = raw.split(mood_match.group(0), 1)[1].strip() if mood_match else raw.strip()
    base_mood = mood_part if mood_part in {"CLEAN", "MESSY", "CHAOTIC"} else "UNKNOWN"
        
    return {
        "name": file_name,
        "mood": base_mood,
        "reason": reason_part,
        "lines": len(lines)
    }

def determine_overall(moods: List[str]) -> str:
    """Return the majority mood label (CLEAN, MESSY, CHAOTIC)."""
    counter = collections.Counter(moods)
    if not counter:
        return "UNKNOWN"
    most_common, _ = counter.most_common(1)[0]
    return most_common

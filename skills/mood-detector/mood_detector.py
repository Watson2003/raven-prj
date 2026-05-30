# mood_detector.py
"""Mood Detector Skill for Raven

Scans source code files in the current working directory, sends each file's content to Claude
and produces a markdown report summarising the "mood" of the project.

Supported extensions: .py, .js, .ts, .jsx, .tsx
Files longer than 500 lines are automatically marked as CHAOTIC.
"""

import os
import pathlib
import collections
import sys
import re
from typing import List, Dict

try:
    import anthropic
except ImportError:  # pragma: no cover
    print("Anthropic SDK not installed. Install with 'pip install anthropic' and set ANTHROPIC_API_KEY.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _get_source_files(root: pathlib.Path) -> List[pathlib.Path]:
    """Return a list of source files under *root* matching supported extensions."""
    patterns = ["**/*.py", "**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx"]
    files = []
    for pattern in patterns:
        files.extend(root.glob(pattern))
    return [f for f in files if f.is_file()]

def _read_file(path: pathlib.Path) -> str:
    """Read the file's content using UTF‑8, falling back to latin‑1 if needed."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")

def _call_claude(content: str, extension: str) -> str:
    """Send *content* to Claude and return the raw response string.

    The prompt asks Claude to rate the mood and give a single‑line reason.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "UNKNOWN - API Key not found"
    
    client = anthropic.Anthropic(api_key=api_key)
    user_message = (
        f"Read this code and rate its mood as one of: CLEAN 😊, MESSY 😤, or CHAOTIC 🤯. "
        f"Give one single line reason why.\n\n```{extension}\n{content}\n```"
    )
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=500,
        temperature=0,
        messages=[{"role": "user", "content": user_message}],
    )
    # The response content may be a list of dicts; handle simple case.
    if isinstance(response.content, list):
        return "".join(part.get("text", "") for part in response.content if isinstance(part, dict))
    return str(response.content)

def _process_file(path: pathlib.Path) -> Dict[str, str]:
    """Analyse *path* and return a dict with keys: 'file', 'mood', 'reason'."""
    lines = path.read_text(errors="ignore").splitlines()
    if len(lines) > 500:
        return {
            "file": str(path),
            "mood": "CHAOTIC 🤯",
            "reason": "File exceeds 500 lines",
        }
    content = _read_file(path)
    ext = path.suffix.lstrip(".")
    raw = _call_claude(content, ext)
    # Robust mood extraction: look for known mood keywords.
    import re
    mood_match = re.search(r"\b(CLEAN|MESSY|CHAOTIC)\b", raw, re.IGNORECASE)
    if mood_match:
        base_mood = mood_match.group(1).upper()
        # Preserve any emoji that follows the mood in the original text.
        emoji_part = re.search(r"(?<=%s)\s*[^\w\s]" % base_mood, raw)
        mood_part = base_mood + (emoji_part.group(0).strip() if emoji_part else "")
        # Reason is whatever follows the first dash or after the mood word.
        split_dash = raw.split("-", 1)
        if len(split_dash) == 2:
            reason_part = split_dash[1].strip()
        else:
            # Remove the mood word from the beginning and use the rest as reason.
            reason_part = raw[mood_match.end():].strip("- –")
    else:
        # Fallback if no mood keyword found.
        parts = raw.split("-", 1)
        if len(parts) == 2:
            mood_part, reason_part = parts[0].strip(), parts[1].strip()
        else:
            tokens = raw.split(maxsplit=1)
            mood_part = tokens[0] if tokens else "UNKNOWN"
            reason_part = tokens[1] if len(tokens) > 1 else ""
    return {
        "file": str(path),
        "mood": mood_part,
        "reason": reason_part,
    }

def _determine_overall(moods: List[str]) -> str:
    """Return the majority mood label (CLEAN, MESSY, CHAOTIC)."""
    counter = collections.Counter(moods)
    if not counter:
        return "UNKNOWN"
    most_common, _ = counter.most_common(1)[0]
    return most_common

# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the mood detector and print a markdown report to STDOUT."""
    curr = pathlib.Path.cwd()
    while curr != curr.parent:
        if (curr / "packages").is_dir() and (curr / "apps").is_dir():
            break
        curr = curr.parent
    
    files = _get_source_files(curr)
    results = [_process_file(f) for f in files]

    # Build markdown report
    md_lines = ["# Project Mood Report", "", "| File | Mood | Reason |", "|---|---|---|"]
    for r in results:
        md_lines.append(f"| `{r['file']}` | {r['mood']} | {r['reason']} |")
    # Compute overall mood using the base label (CLEAN, MESSY, CHAOTIC).
    overall = _determine_overall([re.search(r"\b(CLEAN|MESSY|CHAOTIC)\b", r["mood"], re.IGNORECASE).group(1).upper() if re.search(r"\b(CLEAN|MESSY|CHAOTIC)\b", r["mood"], re.IGNORECASE) else "UNKNOWN" for r in results])
    md_lines.extend(["", f"**Overall Project Mood:** {overall}"])

    report = "\n".join(md_lines)
    print(report)


if __name__ == "__main__":
    main()

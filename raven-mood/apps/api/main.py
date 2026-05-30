from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import zipfile
import tempfile
import os
import pathlib
import urllib.request
import urllib.error
import collections
import re
from typing import List, Dict
import anthropic
from dotenv import load_dotenv
from mood_core import process_file_content, determine_overall

load_dotenv(pathlib.Path(__file__).parent / ".env")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Raven Mood API is running. Please use the frontend at http://localhost:3000"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_codebase(github_url: str = Form(None), file: UploadFile = File(None)):
    if not github_url and not file:
        raise HTTPException(status_code=400, detail="Must provide either a zip file or a github_url")
        
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY environment variable not set")
        
    # Initialize Anthropic client with error handling
    try:
        client = anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        # Catch authentication or any initialization errors and surface a clear HTTP error
        raise HTTPException(status_code=500, detail=f"Failed to initialize Anthropic client: {e}")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        
        if github_url:
            if github_url.endswith("/"):
                github_url = github_url[:-1]
            if github_url.endswith(".git"):
                github_url = github_url[:-4]
            zip_url = f"{github_url}/archive/refs/heads/main.zip"
            zip_path = tmp_path / "repo.zip"
            try:
                urllib.request.urlretrieve(zip_url, zip_path)
            except urllib.error.HTTPError:
                # fallback to master
                zip_url = f"{github_url}/archive/refs/heads/master.zip"
                try:
                    urllib.request.urlretrieve(zip_url, zip_path)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Could not download repository zip: {e}")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Could not download repository zip: {e}")
                
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
            except zipfile.BadZipFile:
                raise HTTPException(status_code=400, detail="Invalid zip file downloaded")
                
        else:
            zip_path = tmp_path / "uploaded.zip"
            content = await file.read()
            with open(zip_path, "wb") as f:
                f.write(content)
                
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(tmpdir)
            except zipfile.BadZipFile:
                raise HTTPException(status_code=400, detail="Uploaded file is not a valid zip archive")

        patterns = ["**/*.py", "**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx"]
        files = []
        for pattern in patterns:
            files.extend(tmp_path.glob(pattern))
            
        supported_files = [f for f in files if f.is_file() and not f.name.endswith(".zip")]
        
        if not supported_files:
            return {
                "overall_mood": "UNKNOWN",
                "files": [],
                "summary": {"clean": 0, "messy": 0, "chaotic": 0}
            }
            
        results = []
        summary = {"clean": 0, "messy": 0, "chaotic": 0}
        
        for f in supported_files:
            try:
                content = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = f.read_text(encoding="latin-1")
            
            # Process file content with graceful handling of Anthropic errors
            try:
                res = process_file_content(f.name, content, client, model="claude-3-5-sonnet-20240620")
            except Exception as e:
                # If the model call fails (e.g., auth error), record the error in the result
                res = {"name": f.name, "mood": "UNKNOWN", "reason": f"API Error: {str(e)}", "lines": len(content.splitlines())}
            
            mood_lower = res["mood"].lower()
            if mood_lower in summary:
                summary[mood_lower] += 1
            elif mood_lower == "unknown":
                pass
            else:
                summary[mood_lower] = summary.get(mood_lower, 0) + 1
                
            results.append(res)
            
        overall_mood = determine_overall([r["mood"] for r in results])
        
        return {
            "overall_mood": overall_mood,
            "files": results,
            "summary": summary
        }

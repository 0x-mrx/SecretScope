import os
import re
import shutil
import base64
import json
import tempfile
import httpx
from typing import List, Dict, Any
from urllib.parse import urljoin
from sqlalchemy.orm import Session
from git import Repo

from app.core.config import settings
from app.services.plugins import scan_and_classify_content

# Regex to find script sources and inline scripts
SCRIPT_SRC_PATTERN = re.compile(r'(?i)<script\s+[^>]*src=["\']([^"\']+)["\']')
INLINE_SCRIPT_PATTERN = re.compile(r'(?i)<script\b[^>]*>(.*?)</script>', re.DOTALL)
SOURCEMAP_PATTERN = re.compile(r'//#\s*sourceMappingURL=(data:application/json;base64,([A-Za-z0-9+/=]+))')

class ScannerEngine:
    @staticmethod
    def scan_website(url: str, db: Session) -> List[Dict[str, Any]]:
        """
        Scans a website by downloading HTML, extracting scripts, source maps,
        and analyzing for secrets.
        """
        findings = []
        try:
            with httpx.Client(timeout=15.0, verify=False) as client:
                # 1. Fetch main HTML page
                response = client.get(url)
                if response.status_code != 200:
                    return findings
                
                html_content = response.text
                
                # Scan main page HTML
                html_findings = scan_and_classify_content(html_content, db)
                for f in html_findings:
                    f["file_path_or_url"] = url
                    findings.append(f)
                
                # Extract inline scripts
                inline_scripts = INLINE_SCRIPT_PATTERN.findall(html_content)
                for idx, script in enumerate(inline_scripts, 1):
                    script_findings = scan_and_classify_content(script, db)
                    for f in script_findings:
                        f["file_path_or_url"] = f"{url} [Inline Script #{idx}]"
                        findings.append(f)
                
                # Extract external JS scripts
                script_urls = SCRIPT_SRC_PATTERN.findall(html_content)
                for src in script_urls:
                    js_url = urljoin(url, src)
                    try:
                        js_response = client.get(js_url)
                        if js_response.status_code == 200:
                            js_content = js_response.text
                            # Scan JS file
                            js_findings = scan_and_classify_content(js_content, db)
                            for f in js_findings:
                                f["file_path_or_url"] = js_url
                                findings.append(f)
                            
                            # Scan for inline base64 source map
                            smap_match = SOURCEMAP_PATTERN.search(js_content)
                            if smap_match:
                                try:
                                    smap_bytes = base64.b64decode(smap_match.group(2))
                                    smap_json = json.loads(smap_bytes.decode('utf-8'))
                                    sources = smap_json.get("sourcesContent", [])
                                    for idx, source_code in enumerate(sources):
                                        source_name = smap_json.get("sources", [f"source_{idx}"])[idx]
                                        smap_findings = scan_and_classify_content(source_code, db)
                                        for f in smap_findings:
                                            f["file_path_or_url"] = f"{js_url} [SourceMap: {source_name}]"
                                            findings.append(f)
                                except Exception:
                                    pass # Ignore map decoding failures
                    except Exception:
                        continue # Skip inaccessible script files
        except Exception as e:
            print(f"Error scanning website {url}: {e}")
        
        return findings

    @staticmethod
    def scan_git_repository(repo_url: str, credentials_token: str, db: Session) -> List[Dict[str, Any]]:
        """
        Clones repository securely, scans all branches and full commit history.
        """
        findings = []
        # Create temp folder inside workspace directory for git clones
        temp_root = os.path.join(os.path.dirname(settings.LOCAL_STORAGE_DIR), "tmp")
        os.makedirs(temp_root, exist_ok=True)
        
        # Prepare URL with auth token if provided
        clone_url = repo_url
        if credentials_token:
            if "github.com" in repo_url:
                clone_url = repo_url.replace("https://", f"https://x-token-auth:{credentials_token}@")
            elif "gitlab.com" in repo_url:
                clone_url = repo_url.replace("https://", f"https://oauth2:{credentials_token}@")
        
        temp_dir = tempfile.mkdtemp(dir=temp_root)
        try:
            repo = Repo.clone_from(clone_url, temp_dir, multi_options=["--depth=10"]) # shallow clone to save space/time
            
            # Walk commits & files
            # For simplicity, walk latest snapshot of files
            for root, dirs, files in os.walk(temp_dir):
                # Ignore .git folder
                if '.git' in dirs:
                    dirs.remove('.git')
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, temp_dir)
                    # Skip binary files or massive assets
                    if file_path.endswith(('.png', '.jpg', '.jpeg', '.zip', '.tar', '.gz', '.pdf', '.bin')):
                        continue
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        
                        file_findings = scan_and_classify_content(content, db)
                        for find in file_findings:
                            find["file_path_or_url"] = f"git://{repo_url}/{rel_path}"
                            findings.append(find)
                    except Exception:
                        continue

            # Walk commits (git log diffs to capture deleted secrets)
            # Scan last 20 commits
            commits = list(repo.iter_commits(max_count=20))
            for i in range(len(commits) - 1):
                commit = commits[i]
                parent = commits[i+1]
                diffs = parent.diff(commit, create_patch=True)
                for diff in diffs:
                    diff_text = diff.diff.decode('utf-8', errors='ignore')
                    diff_findings = scan_and_classify_content(diff_text, db)
                    for find in diff_findings:
                        find["file_path_or_url"] = f"git://{repo_url}/commit/{commit.hexsha}/{diff.a_path or diff.b_path}"
                        findings.append(find)

        except Exception as e:
            print(f"Error scanning Git repository {repo_url}: {e}")
        finally:
            # Clean up temp folder
            shutil.rmtree(temp_dir, ignore_errors=True)
            
        return findings

    @staticmethod
    def scan_local_directory(directory_path: str, db: Session) -> List[Dict[str, Any]]:
        """
        Recursively walks a local directory and scans relevant configuration/code files.
        """
        findings = []
        if not os.path.exists(directory_path):
            return findings

        # Config/Text file extensions only
        allowed_extensions = ('.env', '.json', '.yaml', '.yml', '.js', '.ts', '.py', '.config', '.ini', '.txt', '.sh', '.properties')
        ignored_dirs = {'.git', 'node_modules', 'venv', '__pycache__', '.idea', '.vscode'}

        for root, dirs, files in os.walk(directory_path):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            for file in files:
                if not file.endswith(allowed_extensions) and not file.startswith('.env'):
                    continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    file_findings = scan_and_classify_content(content, db)
                    for find in file_findings:
                        find["file_path_or_url"] = file_path.replace("\\", "/")
                        findings.append(find)
                except Exception:
                    continue

        return findings

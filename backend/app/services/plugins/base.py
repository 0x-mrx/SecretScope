import os
import json
import re
from typing import List, Dict, Any

class BasePlugin:
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
        self.metadata = self._load_metadata()
        self.name = self.metadata.get("name", "Unknown Plugin")
        self.secret_type = self.metadata.get("secret_type", "GENERIC_API_KEY")
        self.default_severity = self.metadata.get("default_severity", "MEDIUM")
        self.description = self.metadata.get("description", "")
        self.patterns = self._compile_patterns()

    def _load_metadata(self) -> Dict[str, Any]:
        meta_path = os.path.join(self.plugin_dir, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                return json.load(f)
        return {}

    def _compile_patterns(self) -> List[re.Pattern]:
        patterns = []
        raw_patterns = self.metadata.get("patterns", [])
        for p in raw_patterns:
            try:
                patterns.append(re.compile(p))
            except re.error as e:
                print(f"Error compiling pattern {p} in plugin {self.name}: {e}")
        return patterns

    def detect(self, content: str) -> List[Dict[str, Any]]:
        """
        Scans content text for candidate secrets.
        Returns a list of dicts: {"match": str, "line": int, "index": int, "context": str}
        """
        results = []
        if not content:
            return results

        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            for pattern in self.patterns:
                for match in pattern.finditer(line):
                    match_str = match.group(0)
                    # Extract surrounding lines for context
                    start_line = max(0, line_num - 2)
                    end_line = min(len(lines), line_num + 2)
                    context_snippet = "\n".join(lines[start_line:end_line])
                    
                    results.append({
                        "match": match_str,
                        "line": line_num,
                        "index": match.start(),
                        "context": context_snippet
                    })
        return results

    def classify(self, match: str, context: str) -> Dict[str, Any]:
        """
        Verifies candidate match and determines confidence (0.0 to 1.0), severity, and masked value.
        Should be overridden by subclass for custom validation.
        """
        # Default implementation
        masked = self.mask_secret(match)
        return {
            "secret_type": self.secret_type,
            "confidence": 0.8,
            "severity": self.default_severity,
            "masked_value": masked,
            "extra_metadata": {}
        }

    def mask_secret(self, secret: str) -> str:
        if len(secret) <= 8:
            return "*" * len(secret)
        return f"{secret[:4]}{'*' * (len(secret) - 8)}{secret[-4:]}"

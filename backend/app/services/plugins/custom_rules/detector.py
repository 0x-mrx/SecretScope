import os
import re
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.services.plugins.base import BasePlugin
from app.models.secret_type import SecretType

class CustomRulesDetector(BasePlugin):
    def __init__(self):
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        super().__init__(plugin_dir)

    def detect_custom(self, content: str, db: Session) -> List[Dict[str, Any]]:
        """
        Queries active custom rules from database and runs them.
        """
        results = []
        if not content or not db:
            return results

        # Fetch custom rules
        custom_types = db.query(SecretType).filter(
            SecretType.is_custom.is_(True),
            SecretType.is_active.is_(True)
        ).all()

        lines = content.splitlines()
        for custom_type in custom_types:
            try:
                pattern = re.compile(custom_type.pattern)
            except re.error:
                continue # Skip invalid pattern
                
            for line_num, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    match_str = match.group(0)
                    start_line = max(0, line_num - 2)
                    end_line = min(len(lines), line_num + 2)
                    context_snippet = "\n".join(lines[start_line:end_line])
                    
                    results.append({
                        "match": match_str,
                        "line": line_num,
                        "index": match.start(),
                        "context": context_snippet,
                        "secret_type_id": custom_type.id,
                        "secret_type_name": custom_type.name,
                        "default_severity": custom_type.description or "MEDIUM" # We store severity/desc
                    })
        return results

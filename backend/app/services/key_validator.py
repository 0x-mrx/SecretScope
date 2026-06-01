import httpx
from typing import Dict, Any

class KeyValidator:
    @staticmethod
    def validate_google_key(key: str) -> Dict[str, Any]:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Pkwy&key={key}"
        try:
            response = httpx.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                if "error_message" in data:
                    err = data["error_message"]
                    if "API key not authorized" in err or "KeyExpired" in err:
                        return {"status": "INVALID", "details": f"Google Maps API rejected key: {err}"}
                    return {"status": "VALID", "details": f"Key is active (restricted): {err}"}
                return {"status": "VALID", "details": "Google Maps API call succeeded. Key is live and active!"}
            else:
                return {"status": "INVALID", "details": f"Google API returned HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "ERROR", "details": f"Connection/validation error: {str(e)}"}

    @staticmethod
    def validate_github_token(token: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"token {token}",
            "User-Agent": "SecretScope-BugHunter"
        }
        try:
            response = httpx.get("https://api.github.com/user", headers=headers, timeout=5.0)
            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get("login", "unknown")
                scopes = response.headers.get("X-OAuth-Scopes", "none")
                return {"status": "VALID", "details": f"GitHub token active. User: {username}, Scopes: {scopes}"}
            elif response.status_code == 401:
                return {"status": "INVALID", "details": "GitHub token is revoked or invalid (401 Unauthorized)"}
            else:
                return {"status": "INVALID", "details": f"GitHub returned HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "ERROR", "details": f"Connection/validation error: {str(e)}"}

    @staticmethod
    def validate_slack_token(token: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        try:
            response = httpx.post("https://slack.com/api/auth.test", headers=headers, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    team = data.get("team", "unknown")
                    user = data.get("user", "unknown")
                    return {"status": "VALID", "details": f"Slack token active. Team: {team}, User: {user}"}
                else:
                    err = data.get("error", "unknown error")
                    return {"status": "INVALID", "details": f"Slack rejected token: {err}"}
            else:
                return {"status": "INVALID", "details": f"Slack API returned HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "ERROR", "details": f"Connection/validation error: {str(e)}"}

    @staticmethod
    def validate_openai_key(key: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {key}"
        }
        try:
            response = httpx.get("https://api.openai.com/v1/models", headers=headers, timeout=5.0)
            if response.status_code == 200:
                return {"status": "VALID", "details": "OpenAI API key active. Succeeded listing models."}
            elif response.status_code == 401:
                return {"status": "INVALID", "details": "OpenAI key is invalid/revoked (401 Unauthorized)"}
            else:
                return {"status": "INVALID", "details": f"OpenAI returned HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "ERROR", "details": f"Connection/validation error: {str(e)}"}

    @classmethod
    def validate_secret(cls, secret_type: str, raw_val: str) -> Dict[str, Any]:
        if secret_type == "GOOGLE_API_KEY":  # nosec B105
            return cls.validate_google_key(raw_val)
        elif secret_type == "GITHUB_TOKEN":  # nosec B105
            return cls.validate_github_token(raw_val)
        elif secret_type == "SLACK_TOKEN":  # nosec B105
            return cls.validate_slack_token(raw_val)
        elif secret_type == "OPENAI_KEY":  # nosec B105
            return cls.validate_openai_key(raw_val)
        else:
            return {"status": "UNSUPPORTED", "details": f"Active validation is not supported yet for {secret_type}."}  # nosec B105

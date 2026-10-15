
import json
import os
import time
import urllib.error
import urllib.request

from app.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        timeout: float = 120.0,
    ):
        self.model = model or os.getenv(
            "OLLAMA_MODEL",
            "qwen2.5:1.5b",
        )
        self.base_url = (
            base_url
            or os.getenv(
                "OLLAMA_BASE_URL",
                "http://localhost:11434",
            )
        ).rstrip("/")
        self.timeout = timeout

    @staticmethod
    def _seconds(value) -> float:
        if not isinstance(value, (int, float)):
            return 0.0
        return value / 1_000_000_000

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        if not isinstance(system_prompt, str) or not system_prompt.strip():
            raise ValueError("System prompt must not be empty.")

        if not isinstance(user_prompt, str) or not user_prompt.strip():
            raise ValueError("User prompt must not be empty.")

        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "options": {"temperature": 0},
        }

        request = urllib.request.Request(
            url=f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        request_started = time.perf_counter()

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                raw_response = response.read().decode("utf-8")

            elapsed = time.perf_counter() - request_started
            result = json.loads(raw_response)

            print(
                "[OLLAMA PERF] "
                f"model={self.model}, "
                f"request={elapsed:.2f}s, "
                f"total={self._seconds(result.get('total_duration')):.2f}s, "
                f"load={self._seconds(result.get('load_duration')):.2f}s, "
                f"prompt={self._seconds(result.get('prompt_eval_duration')):.2f}s, "
                f"generation={self._seconds(result.get('eval_duration')):.2f}s, "
                f"prompt_tokens={result.get('prompt_eval_count', '?')}, "
                f"generated_tokens={result.get('eval_count', '?')}"
            )

            message = result.get("message", {})
            content = message.get("content", "")

            if not isinstance(content, str) or not content.strip():
                raise RuntimeError("Ollama returned an empty response.")

            return content.strip()

        except urllib.error.HTTPError as exc:
            try:
                error_body = exc.read().decode(
                    "utf-8",
                    errors="replace",
                )
            except Exception:
                error_body = ""

            raise RuntimeError(
                f"Ollama HTTP error {exc.code}: "
                f"{error_body or exc.reason}"
            ) from exc

        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Could not connect to Ollama at "
                f"{self.base_url}: {exc.reason}"
            ) from exc

        except TimeoutError as exc:
            raise RuntimeError(
                f"Ollama request timed out after "
                f"{self.timeout:.0f} seconds."
            ) from exc

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Ollama returned an invalid JSON response."
            ) from exc

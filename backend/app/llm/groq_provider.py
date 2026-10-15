import os
import time

from groq import Groq

from app.llm.base import LLMProvider


class GroqProvider(LLMProvider):
    """Hosted LLM provider using the Groq API."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.model = model or os.getenv(
            "GROQ_MODEL",
            "llama-3.1-8b-instant",
        )
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY is missing. Add it to your project .env file."
            )

        self.client = Groq(
            api_key=self.api_key,
            timeout=timeout,
        )

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response using Groq chat completions."""

        if not system_prompt or not system_prompt.strip():
            raise ValueError("system_prompt cannot be empty.")

        if not user_prompt or not user_prompt.strip():
            raise ValueError("user_prompt cannot be empty.")

        started = time.perf_counter()

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=0,
                max_tokens=1024,
            )

            elapsed = time.perf_counter() - started

            usage = completion.usage
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0

            print(
                f"[GROQ PERF] model={self.model}, "
                f"total={elapsed:.2f}s, "
                f"prompt_tokens={prompt_tokens}, "
                f"completion_tokens={completion_tokens}"
            )

            if not completion.choices:
                raise RuntimeError("Groq returned no completion choices.")

            content = completion.choices[0].message.content

            if not content or not content.strip():
                raise RuntimeError("Groq returned an empty response.")

            return content.strip()

        except Exception as exc:
            if isinstance(exc, (ValueError, RuntimeError)):
                raise

            elapsed = time.perf_counter() - started
            raise RuntimeError(
                f"Groq API request failed after {elapsed:.2f}s: "
                f"{type(exc).__name__}: {exc}"
            ) from exc
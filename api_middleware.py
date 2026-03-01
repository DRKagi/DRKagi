# coding: utf-8
"""
DRKagi API Key Middleware v2
Rotates through multiple Groq API keys with automatic cooldown recovery.
"""

import random
import time
import os
from groq import Groq

class APIMiddleware:
    """
    Manages a pool of Groq API keys and rotates them intelligently.
    Features: round-robin, random, least-used strategies + auto-cooldown.
    """

    def __init__(self):
        self.keys = self._load_keys()
        self.current_index = 0
        self.failed_keys = set()
        self.usage_counts = {k: 0 for k in self.keys}
        self.total_requests = 0
        self.total_errors = 0

    def _load_keys(self):
        """Load API keys from config (which includes hardcoded fallback pool)."""
        from config import config as cfg
        keys_str = cfg.GROQ_API_KEYS
        if keys_str:
            keys = [k.strip() for k in keys_str.split(",") if k.strip()]
            if keys:
                return keys
        # Last resort — single key
        if cfg.GROQ_API_KEY:
            return [cfg.GROQ_API_KEY]
        raise ValueError("No Groq API keys found. Check config.py or set GROQ_API_KEY in .env")

    def get_client(self, strategy="least_used"):
        """Get a Groq client using a rotation strategy."""
        available = [k for k in self.keys if k not in self.failed_keys]
        if not available:
            self.failed_keys.clear()
            available = self.keys

        if strategy == "random":
            key = random.choice(available)
        elif strategy == "least_used":
            key = min(available, key=lambda k: self.usage_counts.get(k, 0))
        else:  # round_robin
            key = available[self.current_index % len(available)]
            self.current_index += 1

        self.usage_counts[key] = self.usage_counts.get(key, 0) + 1
        return Groq(api_key=key), key

    def mark_key_failed(self, key, reason="rate_limit"):
        """Mark a key as temporarily unavailable."""
        if len(self.keys) > 1:
            self.failed_keys.add(key)

    def make_request(self, model, messages, response_format=None, temperature=0.2, max_tokens=4096):
        """
        Make an API request with automatic key rotation + cooldown recovery.
        Instead of crashing when all keys fail, waits and retries.
        """
        max_attempts = len(self.keys) + 1
        max_cooldowns = 3  # retry up to 3 cooldown cycles
        last_error = None

        for cooldown_round in range(max_cooldowns):
            for attempt in range(max_attempts):
                client, current_key = self.get_client()
                try:
                    kwargs = {
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    }
                    if response_format:
                        kwargs["response_format"] = response_format

                    completion = client.chat.completions.create(**kwargs)
                    self.total_requests += 1
                    return completion.choices[0].message.content

                except Exception as e:
                    error_str = str(e).lower()
                    last_error = e
                    self.total_errors += 1

                    if "rate_limit" in error_str or "429" in error_str:
                        self.mark_key_failed(current_key, "rate_limit")
                        time.sleep(1)
                        continue
                    elif "invalid_api_key" in error_str or "authentication" in error_str:
                        self.mark_key_failed(current_key, "invalid_key")
                        continue
                    elif "403" in error_str or "access denied" in error_str:
                        # Tor exit node blocked by Groq API
                        raise Exception(
                            "AI Error: Groq API blocked this connection (403).\n"
                            "  Cause: AnonSurf/Tor exit nodes are blocked by Groq.\n"
                            "  Fix:   Use 'drkagi-anon' instead of 'drkagi' when AnonSurf is active.\n"
                            "         sudo drkagi-anon"
                        )
                    else:
                        raise

            # All keys exhausted — cooldown instead of crashing
            if cooldown_round < max_cooldowns - 1:
                wait = 30 * (cooldown_round + 1)
                print(f"\n[!] All API keys rate-limited. Cooling down {wait}s...")
                for remaining in range(wait, 0, -1):
                    print(f"\r    Retrying in {remaining}s...  ", end="", flush=True)
                    time.sleep(1)
                print("\r    Retrying now...              ")
                self.failed_keys.clear()  # Reset and try again

        raise Exception(f"All API keys exhausted after {max_cooldowns} cooldown cycles. Last error: {last_error}")

    def get_status(self):
        """Return middleware status info."""
        return {
            "total_keys": len(self.keys),
            "active_keys": len(self.keys) - len(self.failed_keys),
            "failed_keys": len(self.failed_keys),
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "usage_counts": dict(self.usage_counts)
        }

    def reset(self):
        """Reset all failed keys and counters."""
        self.failed_keys.clear()


# Singleton instance
_middleware_instance = None

def get_middleware():
    """Get or create the global middleware instance."""
    global _middleware_instance
    if _middleware_instance is None:
        from dotenv import load_dotenv
        load_dotenv()
        _middleware_instance = APIMiddleware()
    return _middleware_instance

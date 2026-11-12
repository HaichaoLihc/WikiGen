"""The agent runtime: OpenAI's Codex coding agent, running read-only inside the repository.

An Agent is one conversation with memory. `agent.session` identifies it, so a later run can continue it.
"""
import os
import threading
from collections import Counter
from functools import cache
from pathlib import Path

from openai_codex import ApprovalMode, Codex, CodexConfig, Sandbox

usage = Counter()  # tokens per model, e.g. usage["gpt-x input"]
_lock = threading.Lock()

# USD per million tokens (input, cached input, output), from OpenAI's pricing page in November 2026.
# Requests over 272k input tokens cost double; that surcharge is not modelled here.
PRICES = {"gpt-6.1-sol": (2.00, 0.10, 10.00), "gpt-6.1-terra": (1.00, 0.05, 5.00)}


@cache
def api_key_home():
    """With OPENAI_API_KEY set, Codex bills that key. It then uses its own settings folder, so your
    normal Codex login is left untouched. Returns that folder, or None to use the normal login."""
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    home = Path(".codex-home").resolve()
    home.mkdir(exist_ok=True)
    codex = Codex(CodexConfig(env={**os.environ, "CODEX_HOME": str(home)}))
    codex.login_api_key(key)
    codex.close()
    return home


class Agent:
    def __init__(self, system, repo, model=None, session=None):
        home = api_key_home()
        # One Codex process per agent, so agents can run in parallel.
        self.codex = Codex(CodexConfig(env={**os.environ, "CODEX_HOME": str(home)})) if home else Codex()
        self.model = model
        options = dict(cwd=str(repo), model=model, developer_instructions=system,
                       sandbox=Sandbox.read_only, approval_mode=ApprovalMode.deny_all)
        self.thread = self.codex.thread_resume(session, **options) if session else self.codex.thread_start(**options)
        self.session = self.thread.id
        self.counted = Counter()

    def ask(self, prompt, schema=None):
        """Send one message and return the agent's final answer (JSON text when a schema is given)."""
        result = self.thread.run(prompt, output_schema=schema)
        if result.usage:
            # Codex reports running totals for the conversation; count only what this turn added.
            total = result.usage.total
            name = self.model or "codex-default"
            now = Counter({f"{name} input": total.input_tokens, f"{name} cached input": total.cached_input_tokens,
                           f"{name} output": total.output_tokens})
            with _lock:
                usage.update(now - self.counted)
            self.counted = now
        return result.final_response or ""


def ask_checked(agent, prompt, check, schema=None, retries=2):
    """Ask, then send the answer's problems back until `check(answer)` finds none or retries run out."""
    answer = agent.ask(prompt, schema)
    for _ in range(retries):
        found = check(answer)
        if not found:
            break
        answer = agent.ask("Problems with your answer:\n" + "\n".join(found)
                           + "\nReply with the full corrected version only.", schema)
    return answer


def estimated_cost():
    """Dollar estimate when billing an API key; None on a Codex login, which draws on a ChatGPT plan instead."""
    if not api_key_home():
        return None
    total = 0.0
    for model, (input_price, cached_price, output_price) in PRICES.items():
        cached = usage[f"{model} cached input"]
        total += ((usage[f"{model} input"] - cached) * input_price + cached * cached_price
                  + usage[f"{model} output"] * output_price) / 1e6
    return round(total, 2)

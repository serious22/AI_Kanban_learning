"""Subagents: Topic 2 (isolation + parallel) and Topic 3 (structured failures)."""

# Topic 2: role -> {"system": str, "tools": [tool dicts]}  (DIY AgentDefinition)
SUBAGENT_ROLES: dict[str, dict] = {}

# Topic 2: tool the coordinator calls; description must say "sees nothing of this
# conversation" + "call several times in the SAME response to run in parallel".
SPAWN_SUBAGENT: dict = {}

# Topic 3: JSON shape every subagent must return (status / error_type / attempted /
# findings[{claim, source_url, published_date}] / suggested_alternative).
SUBAGENT_RESULT_FORMAT = ""


def run_subagent(role: str, prompt: str) -> str:
    """Topic 2. Fresh messages=[{"role":"user","content": prompt}] -> run_agent(...)
    -> return ONLY the final text. Topic 3: on failure return a structured failure JSON."""
    raise NotImplementedError("Topic 2: run_subagent")


def make_coordinator_handler(card, state):
    """Topic 2. Like tools.make_tool_handler, but all spawn_subagent blocks in one
    response run in PARALLEL (ThreadPoolExecutor) and each gets its tool_result."""
    raise NotImplementedError("Topic 2: make_coordinator_handler")

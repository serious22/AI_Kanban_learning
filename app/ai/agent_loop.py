"""The agent loop: Topic 1 (+ Topic 6 forced tool_choice, Topic 15 case facts)."""
from __future__ import annotations
from dataclasses import dataclass
from app.models import Card, Outcome

MODEL = "claude-sonnet-5-5"     # check the current model id in the docs before you run


@dataclass
class AgentRun:
    messages: list
    stop_reason: str            # "end_turn" | "max_tokens" | "step_limit"
    final_text: str


def run_agent(system: str, tools: list, messages: list, handle_tools, max_steps: int = 25) -> AgentRun:
    """Topic 1. The generic loop. Knows nothing about cards (subagents reuse it).

    loop up to max_steps (a SAFETY NET, not the control flow):
        resp = client.messages.create(...)
        append assistant turn (content blocks as dicts: b.model_dump(exclude_none=True))
        stop_reason == "tool_use" -> append ONE user message with handle_tools(calls); continue
        otherwise return AgentRun(messages, resp.stop_reason, text)
    return AgentRun(messages, "step_limit", "")
    """

    for _ in range(max_steps):                                  # ①
        resp = client.messages.create(model=MODEL, max_tokens=4096,
                                      system=system, tools=tools, messages=messages)
        messages.append({"role": "assistant",                   # ②
                         "content": [b.model_dump(exclude_none=True) for b in resp.content]})

        if resp.stop_reason == "tool_use":                      # ③
            calls = [b for b in resp.content if b.type == "tool_use"]
            messages.append({"role": "user", "content": handle_tools(calls)})
            continue

        text = "".join(b.text for b in resp.content if b.type == "text")
        return AgentRun(messages, resp.stop_reason, text)       # ④ end_turn / max_tokens

    return AgentRun(messages, "step_limit", "")


def run_task(card: Card, messages: list | None = None) -> Outcome:
    """Topic 1. Run the card agent and turn the run into an Outcome.

    - default messages = [{"role": "user", "content": build_task_prompt(card)}]
    - store.save_transcript(card.id, run.messages)        (Topic 4 needs it)
    - max_tokens / step_limit -> Outcome("human_qa", reason)
    - else -> router.route_card(card, state["result"])
    """
    state = {"result": None}
    messages = messages or [{"role": "user", "content": build_task_prompt(card)}]
    run = run_agent(SYSTEM_PROMPT, TOOLS, messages, make_tool_handler(card, state))
    store.save_transcript(card.id, run.messages)                # ①

    if run.stop_reason == "max_tokens":
        return Outcome("human_qa", "Output was cut off (max_tokens)")
    if run.stop_reason == "step_limit":
        return Outcome("human_qa", "Hit the step limit without finishing")
    return route_card(card, state["result"])

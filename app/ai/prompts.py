"""Prompts: Topic 1 (task prompt) and Topic 12 (system prompt)."""
from app.models import Card

# Topic 12: role + explicit open_questions criteria + 2-4 examples + output contract.
SYSTEM_PROMPT = ""


def build_task_prompt(card: Card) -> str:
    """Topic 1. Turn the card into the agent's FIRST user message.

    Must include: title, task_type, description and EVERY comment in order
    (author + timestamp), wrapped in XML tags. Tell Claude later comments win
    on conflict and that it must finish by calling finish_task exactly once.
    """
    comments = "\n".join(                                   # ①
        f'<comment n="{i}" author="{c.author}" at="{c.created_at}">{c.text}</comment>'
        for i, c in enumerate(card.comments, 1)
    )
    return f"""<task>
<title>{card.title}</title>
<type>{card.task_type or "general"}</type>
<description>{card.description}</description>
<comments>
{comments}
</comments>
</task>

Do this task. Later comments override earlier ones if they conflict.   # ②
Post short progress notes with add_comment.
When finished, call finish_task exactly once."""  

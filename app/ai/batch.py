"""Nightly digest with the Message Batches API: Topic 14."""


def submit_nightly_digest(cards) -> str:
    """Topic 14. client.messages.batches.create(requests=[{custom_id: f"card-{id}", params: {...}}])
    -> return batch.id"""
    raise NotImplementedError("Topic 14: submit_nightly_digest")


def collect_digest(batch_id: str) -> dict[int, str] | None:
    """Topic 14. None until processing_status == "ended"; match results by custom_id;
    resubmit ONLY failed ones."""
    raise NotImplementedError("Topic 14: collect_digest")

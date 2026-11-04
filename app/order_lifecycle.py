"""Pure order lifecycle rules for future route integration."""

TRANSITIONS = {
    "pending": frozenset({"under_review", "rejected"}),
    "under_review": frozenset({"in_progress", "waiting_documents", "rejected"}),
    "waiting_documents": frozenset({"under_review", "rejected"}),
    "in_progress": frozenset({"completed", "waiting_documents", "rejected"}),
    "completed": frozenset(),
    "rejected": frozenset(),
}


def validate_order_transition(current, target):
    if current not in TRANSITIONS or target not in TRANSITIONS:
        raise ValueError("Unknown order status")
    if target not in TRANSITIONS[current]:
        raise ValueError("Order status transition is not allowed")
    return target

def grade_easy(completed_tickets, budget_spent):
    # Agent should only close tickets. No refunds. No escalations.
    score = 0.0
    for t in completed_tickets:
        if t.status == 'closed' and t.refund_amount == 0.0:
            score += (1.0 / max(len(completed_tickets), 1))
    return round(max(0.0, min(1.0, score)), 2)

def grade_medium(completed_tickets, budget_spent):
    # Agent should refund exactly based on policies (delayed orders get $20)
    score = 0.0
    for t in completed_tickets:
        if "delayed" in t.issue_type:
            if t.status == 'closed' and t.refund_amount == 20.0:
                score += (1.0 / max(len(completed_tickets), 1))
        else:
            if t.status == 'closed' and t.refund_amount == 0.0:
                score += (1.0 / max(len(completed_tickets), 1))
    return round(max(0.0, min(1.0, score)), 2)

def grade_hard(completed_tickets, budget_spent):
    # Mixed scenario: Bug ticket escalated, delayed gets $20 refund, abuse gets 0 refund
    score = 0.0
    penalty = 0.0
    if budget_spent > 100.0:
        penalty = 0.5
    for t in completed_tickets:
        if t.issue_type == "bug":
            if t.status == 'escalated':
                score += (1.0 / max(len(completed_tickets), 1))
        elif t.issue_type == "abuse":
            if t.status == 'closed' and t.refund_amount == 0.0:
                score += (1.0 / max(len(completed_tickets), 1))
        elif t.issue_type == "delayed_order":
            if t.status == 'closed' and t.refund_amount == 20.0:
                score += (1.0 / max(len(completed_tickets), 1))
    final_score = max(0.0, min(1.0, score - penalty))
    return round(final_score, 2)

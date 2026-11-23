#!/usr/bin/env bash
# The review config says specs live in product/requirements/ and that the latest
# version is on main. The branch feature/gift-cards was cut before main added
# requirement 3 (an over-limit redeem raises ValueError); the branch does not raise.
set -euo pipefail
export GIT_AUTHOR_NAME=Eval GIT_AUTHOR_EMAIL=eval@example.com
export GIT_COMMITTER_NAME=Eval GIT_COMMITTER_EMAIL=eval@example.com
git init -q -b main
mkdir -p src docs/agents product/requirements
cat > AGENTS.md <<'MD'
# Agent instructions

## Agent skills

### Code review

Review config for `daedalus-core:code-review`. See `docs/agents/code-review.md`.
MD
cat > docs/agents/code-review.md <<'MD'
# Code review

## Spec sources

- Feature specs live in `product/requirements/<feature>.md`, named after the branch without its `feature/` prefix. Product edits them on `main`, so read the latest version from there: `git show main:product/requirements/<feature>.md`.
MD
cat > product/requirements/gift-cards.md <<'MD'
# Gift cards

## Requirements

1. `redeem(balance_cents, amount_cents)` in `src/gift_cards.py` returns the balance left after redeeming `amount_cents`, in integer cents.
2. Redeeming a negative amount raises `ValueError`.
MD
cat > src/gift_cards.py <<'PY'
"""Gift cards."""
PY
git add -A
git commit -qm "Add gift card spec and the review config"
git switch -qc feature/gift-cards
cat >> src/gift_cards.py <<'PY'


def redeem(balance_cents, amount_cents):
    """Return the balance left after redeeming amount_cents."""
    if amount_cents < 0:
        raise ValueError("amount_cents must not be negative")
    return max(balance_cents - amount_cents, 0)
PY
git commit -qam "Add redeem"
git switch -q main
cat >> product/requirements/gift-cards.md <<'MD'
3. Redeeming more than the balance raises `ValueError` and leaves the balance unchanged.
MD
git commit -qam "Gift cards: reject over-limit redemptions"
git switch -q feature/gift-cards

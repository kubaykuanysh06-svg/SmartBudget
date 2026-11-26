"""Reject non-positive money amounts at the database level.

The API already validates amounts; these CHECK constraints make sure no other
path (scripts, manual SQL, future code) can store a zero or negative amount.

They are created NOT VALID so the upgrade never fails on rows that already
exist in a running database: PostgreSQL enforces them for every new or
updated row, without scanning old ones. Validate later, once old data is
known to be clean, with ALTER TABLE ... VALIDATE CONSTRAINT.
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

_CHECKS = (
    ("transactions", "ck_transactions_amount_positive", "amount > 0"),
    ("recurring_transactions", "ck_recurring_transactions_amount_positive", "amount > 0"),
    ("budgets", "ck_budgets_limit_amount_positive", "limit_amount > 0"),
)


def upgrade() -> None:
    for table, name, condition in _CHECKS:
        op.execute(f"ALTER TABLE {table} ADD CONSTRAINT {name} CHECK ({condition}) NOT VALID")


def downgrade() -> None:
    for table, name, _ in reversed(_CHECKS):
        op.execute(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {name}")

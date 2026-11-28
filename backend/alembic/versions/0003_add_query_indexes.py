"""Add query indexes on user_id and transaction dates."""

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_transactions_user_id_date",
        "transactions",
        ["user_id", "transaction_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_categories_user_id"), "categories", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_budgets_user_id"), "budgets", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_ai_insights_user_id"), "ai_insights", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_recurring_transactions_user_id"),
        "recurring_transactions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_price_history_user_id"), "price_history", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_price_history_user_id"), table_name="price_history")
    op.drop_index(
        op.f("ix_recurring_transactions_user_id"), table_name="recurring_transactions"
    )
    op.drop_index(op.f("ix_ai_insights_user_id"), table_name="ai_insights")
    op.drop_index(op.f("ix_budgets_user_id"), table_name="budgets")
    op.drop_index(op.f("ix_categories_user_id"), table_name="categories")
    op.drop_index("ix_transactions_user_id_date", table_name="transactions")

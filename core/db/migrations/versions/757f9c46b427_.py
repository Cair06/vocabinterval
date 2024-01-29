"""

Revision ID: 757f9c46b427
Revises: cc0a7e275656
Create Date: 2024-01-29 14:52:03.477630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '757f9c46b427'
down_revision: Union[str, None] = 'cc0a7e275656'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Команда для добавления каскадного удаления
    op.drop_constraint('repetitions_card_id_fkey', 'repetitions', type_='foreignkey')
    op.create_foreign_key('repetitions_card_id_fkey', 'repetitions', 'cards', ['card_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # Команда для отмены каскадного удаления
    op.drop_constraint('repetitions_card_id_fkey', 'repetitions', type_='foreignkey')
    op.create_foreign_key('repetitions_card_id_fkey', 'repetitions', 'cards', ['card_id'], ['id'])
    # ### end Alembic commands ###
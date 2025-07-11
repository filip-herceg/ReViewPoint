# Migration Script Template (script.py.mako)

This file is a Mako template used by Alembic to generate new database migration scripts. It provides the standard structure and boilerplate code for all migration files.

## Overview

The `script.py.mako` template is automatically used when creating new migrations with commands like:
```bash
python -m alembic revision --autogenerate -m "description"
```

## Template Structure

The template generates migration files with the following structure:

### Header Section
```python
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
```

- **message**: Description provided when creating the migration
- **up_revision**: Unique identifier for this migration
- **down_revision**: Previous migration ID (for chaining)
- **create_date**: Timestamp when migration was created

### Import Section
```python
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}
```

Standard imports needed for most migrations:
- `alembic.op`: Operations for schema changes
- `sqlalchemy as sa`: SQLAlchemy types and functions
- Additional imports are added automatically based on detected changes

### Revision Metadata
```python
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}
```

Metadata used by Alembic to:
- Track migration order and dependencies
- Handle branching and merging of migration chains
- Validate migration consistency

### Upgrade Function
```python
def upgrade() -> None:
    """Upgrade schema."""
    ${upgrades if upgrades else "pass"}
```

Contains the operations to apply the migration:
- Create/alter/drop tables
- Add/modify/remove columns
- Create/drop indexes
- Insert/update/delete data (when necessary)

### Downgrade Function
```python
def downgrade() -> None:
    """Downgrade schema."""
    ${downgrades if downgrades else "pass"}
```

Contains the operations to reverse the migration:
- Should undo all changes made in `upgrade()`
- Critical for rollback capabilities
- Often the reverse of upgrade operations

## Template Variables

The Mako template uses several variables that are populated by Alembic:

| Variable | Description | Example |
|----------|-------------|---------|
| `${message}` | Migration description | "Add user email index" |
| `${up_revision}` | Current revision ID | "abc123def456" |
| `${down_revision}` | Previous revision ID | "def456ghi789" |
| `${create_date}` | Creation timestamp | "2025-07-11 10:30:00.123456" |
| `${upgrades}` | Auto-generated upgrade operations | `op.create_table(...)` |
| `${downgrades}` | Auto-generated downgrade operations | `op.drop_table(...)` |
| `${imports}` | Additional required imports | Custom type imports |
| `${branch_labels}` | Branch labels (for complex scenarios) | None (usually) |
| `${depends_on}` | Dependencies (for complex scenarios) | None (usually) |

## Common Operations Generated

### Table Operations
```python
# Create table
op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(255), nullable=False),
    sa.PrimaryKeyConstraint('id')
)

# Drop table
op.drop_table('users')
```

### Column Operations
```python
# Add column
op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

# Alter column
op.alter_column('users', 'email', nullable=False)

# Drop column
op.drop_column('users', 'phone')
```

### Index Operations
```python
# Create index
op.create_index('ix_users_email', 'users', ['email'])

# Drop index
op.drop_index('ix_users_email', table_name='users')
```

### Foreign Key Operations
```python
# Create foreign key
op.create_foreign_key('fk_posts_user_id', 'posts', 'users', ['user_id'], ['id'])

# Drop foreign key
op.drop_constraint('fk_posts_user_id', 'posts', type_='foreignkey')
```

## Customization

The template can be customized to:
- Add standard imports for your project
- Include custom validation or logging
- Add project-specific metadata
- Modify the function signatures or documentation

## Best Practices

1. **Keep the template simple** - complex logic should be in individual migrations
2. **Include type hints** - helps with code quality and IDE support
3. **Use descriptive docstrings** - makes generated code self-documenting
4. **Maintain consistency** - all migrations should follow the same pattern
5. **Review generated code** - always check auto-generated migrations before applying

## Example Generated Migration

When you run `python -m alembic revision --autogenerate -m "Add user profile table"`, the template generates:

```python
"""Add user profile table

Revision ID: a1b2c3d4e5f6
Revises: f140e6f46727
Create Date: 2025-07-11 10:30:00.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f140e6f46727'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('user_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('user_profiles')
```

This template ensures consistency across all migration files and provides a solid foundation for database schema evolution.
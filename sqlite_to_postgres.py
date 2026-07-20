from core.config import *

from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker

# ------------------------------------------------------------------
# SOURCE
# ------------------------------------------------------------------

SQLITE_URL = "sqlite:///C:/SwarmLead-AI/data/swarmlead.db"

# ------------------------------------------------------------------
# TARGET
# ------------------------------------------------------------------

POSTGRES_URL = "postgresql://swarm:SwarmLead2026!@localhost:5432/swarm"

# ------------------------------------------------------------------
# ENGINES
# ------------------------------------------------------------------

sqlite_engine = create_engine(SQLITE_URL)
postgres_engine = create_engine(POSTGRES_URL)

sqlite_meta = MetaData()
postgres_meta = MetaData()

sqlite_meta.reflect(bind=sqlite_engine)
postgres_meta.reflect(bind=postgres_engine)

# ------------------------------------------------------------------
# TABLES TO MIGRATE
# ------------------------------------------------------------------

TABLE_ORDER = [
    "users",
    "company_tenants",
    "leads",
    "notifications",
    "workflows",
    "workflow_steps",
    "tickets",
    "ticket_history",
    "ticket_comments",
    "message_threads",
    "messages",
    "usage_events",
    "api_keys",
    "deployments",
]

# ------------------------------------------------------------------
# MIGRATION
# ------------------------------------------------------------------

for table_name in TABLE_ORDER:
    if table_name not in sqlite_meta.tables:
        print(f"[SKIP] {table_name} not found in SQLite")
        continue

    if table_name not in postgres_meta.tables:
        print(f"[SKIP] {table_name} not found in PostgreSQL")
        continue

    sqlite_table = sqlite_meta.tables[table_name]
    postgres_table = postgres_meta.tables[table_name]

    print(f"\nMigrating {table_name}")

    with sqlite_engine.connect() as source:
        rows = source.execute(select(sqlite_table)).mappings().all()

    if not rows:
        print(f"  No rows found")
        continue

    inserted = 0
    skipped = 0

    with postgres_engine.begin() as target:
        for row in rows:
            try:
                target.execute(postgres_table.insert().values(**dict(row)))

                inserted += 1

            except Exception:
                skipped += 1

    print(f"  Inserted: {inserted}")

    print(f"  Skipped: {skipped}")

print("\nMigration complete")

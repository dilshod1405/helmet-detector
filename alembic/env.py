from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
import pgvector.sqlalchemy.vector

from alembic import context

# .env faylidan muhit o'zgaruvchilarini yuklash
import os
from dotenv import load_dotenv
load_dotenv()

# Bizning loyiha sozlamalarimizni import qilish
from app.core.config import settings
from app.db.database import Base # Base ni import qilish
from app.db.models import Employee, Incident # Barcha modellarni import qilish

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata

# <<<< BU YERDAN YANGI KOD BOSHLANADI >>>>

def render_item(type_, obj, autogen_context):
    """Provide a rendering method to produce a more concise output."""
    if type_ == "type" and isinstance(obj, pgvector.sqlalchemy.vector.VECTOR):
        # pgvector.sqlalchemy.vector.VECTOR turini ko'rganda, uni to'g'ri render qilish
        # va kerakli importni qo'shish
        autogen_context.imports.add("import pgvector.sqlalchemy.vector")
        return f"pgvector.sqlalchemy.vector.VECTOR(dim={obj.dim})"
    # Boshqa turlar uchun standart renderlashni ishlatish
    return False

# <<<< YANGI KOD SHU YERDA TUGAYDI >>>>

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_item=render_item, # <<<< render_item ni bu yerga qo'shing
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            render_item=render_item, # <<<< render_item ni bu yerga qo'shing
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

import os
import subprocess
import sys


def init_alembic():
    try:
        if os.path.exists('migrations'):
            return

        subprocess.run(["alembic", "init", "migrations"], check=True)

        env_py_path = 'migrations/env.py'
        with open(env_py_path, 'r') as file:
            content = file.read()

        import_line = "from recommendation_models import Base\n"
        target_metadata_line = "target_metadata = Base.metadata\n"

        content = content.replace("target_metadata = None", target_metadata_line)

        import_section_end = "from alembic import context\n"
        content = content.replace(import_section_end, import_section_end + "\n" + import_line)

        old_run_migrations_online = """def run_migrations_online() -> None:
    \"\"\"Run migrations in 'online' mode.\"\"\"
    connectable = engine_from_config(
        config.get_section(config.config_file_name),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )"""

        new_run_migrations_online = """def run_migrations_online() -> None:
    \"\"\"Run migrations in 'online' mode.\"\"\"
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}

    url = config.get_main_option("sqlalchemy.url")
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=url
    )"""

        content = content.replace(old_run_migrations_online, new_run_migrations_online)

        with open(env_py_path, 'w') as file:
            file.write(content)

        print("Alembic успешно инициализирован и настроен!")

    except subprocess.CalledProcessError as e:
        print(f"Ошибка при инициализации Alembic: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_alembic()
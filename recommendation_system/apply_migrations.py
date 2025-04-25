import subprocess
import sys
import os


def apply_migrations():
    try:
        if not os.path.exists('alembic.ini'):
            print("Ошибка: Файл alembic.ini не найден!")
            sys.exit(1)

        if not os.path.exists('migrations'):
            print("Ошибка: Директория migrations не найдена!")
            sys.exit(1)

        if not os.path.exists('migrations/env.py'):
            print("Ошибка: Файл migrations/env.py не найден!")
            sys.exit(1)

        subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True
        )

    except subprocess.CalledProcessError as e:
        print(f"Ошибка при применении миграций: {e}")
        print("Вывод команды:")
        print(e.stdout)
        print("Ошибки:")
        print(e.stderr)
        sys.exit(1)


if __name__ == "__main__":
    apply_migrations()
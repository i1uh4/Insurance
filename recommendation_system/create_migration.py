import subprocess
import sys

def create_initial_migration():
    try:
        print("Создание начальной миграции...")
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "initial_migration"],
            check=True,
            capture_output=True,
            text=True
        )
        print("Вывод команды alembic:")
        print(result.stdout)
        print("Начальная миграция успешно создана!")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании миграции: {e}")
        print("Вывод команды:")
        print(e.stdout)
        print("Ошибки:")
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    create_initial_migration()
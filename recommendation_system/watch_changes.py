import time
import os
import hashlib
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def _get_file_hash(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


class ModelChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = {}

    def on_modified(self, event):
        if event.is_directory:
            return

        if event.src_path.endswith('.py') and 'recommendation_models.py' in event.src_path:
            file_hash = _get_file_hash(event.src_path)

            # Проверяем, изменился ли файл на самом деле
            if event.src_path in self.last_modified and self.last_modified[event.src_path] == file_hash:
                return

            self.last_modified[event.src_path] = file_hash
            print(f"Обнаружены изменения в {event.src_path}. Создаем миграцию...")

            # Автоматически создаем миграцию
            try:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                migration_name = f"{timestamp}_auto_migration"
                subprocess.run(
                    ["alembic", "revision", "--autogenerate", "-m", migration_name],
                    check=True,
                    capture_output=True,
                    text=True
                )

                subprocess.run(
                    ["alembic", "upgrade", "head"],
                    check=True,
                    capture_output=True,
                    text=True
                )

            except subprocess.CalledProcessError as e:
                print(f"Ошибка при работе с миграцией: {e}")
                print("Вывод команды:")
                print(e.stdout)
                print("Ошибки:")
                print(e.stderr)


def watch_models():
    event_handler = ModelChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    try:
        print("Отслеживание изменений в моделях рекомендательной системы запущено...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    watch_models()
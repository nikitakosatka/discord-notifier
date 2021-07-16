import json


class Config(dict):
    FILE_NAME = "notifier-settings.json"

    def __init__(self):
        super().__init__()
        try:
            with open(self.FILE_NAME) as f:
                self.update(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError):  # Файл не существовал
            pass

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._save()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._save()

    def _save(self):
        with open(self.FILE_NAME, "w+") as f:
            json.dump(self, f, indent=2)

    def __del__(self):
        self._save()

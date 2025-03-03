class MissingEntry(Exception):
    def __init__(self, object_type: str, object_id):
        self.object_type = object_type
        self.object_id = object_id

    def __str__(self):
        return f"Missing {self.object_type} ({self.object_id})"


class DuplicateEntry(Exception):
    def __init__(self, object_type: str, object_id):
        self.object_type = object_type
        self.object_id = object_id

    def __str__(self):
        return f"Duplicate {self.object_type} ({self.object_id})"

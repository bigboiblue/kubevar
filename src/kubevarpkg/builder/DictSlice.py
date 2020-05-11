class DictSlice:
    def __init__(self, variant: str, start: int, end: int, key_path: list):
        self.type = variant
        self.start = start
        self.end = end
        self.key_path = key_path

    def overlaps(self, start: int, end: int) -> bool:
        return self.start < start < self.end or self.start < end < self.end

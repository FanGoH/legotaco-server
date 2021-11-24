class Filling:
    def __init__(self, max_, available=None, name="Default Filling"):
        if available is None:
            available = max_

        self.max = max_
        self.available = available
        self.name = name

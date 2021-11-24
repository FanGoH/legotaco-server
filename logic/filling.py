class Filling:

    def __init__(self, max_, available=None):
        if available is None:
            available = max_

        self.max = max_
        self.available = available
        pass

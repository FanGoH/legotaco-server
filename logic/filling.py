class Filling:
    def __init__(self, max_, available=None, name="Default Filling", to="No one"):
        if available is None:
            available = max_

        self.max = max_
        self.available = available
        self.name = name
        self.to=to

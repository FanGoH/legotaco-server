class RoundRobin:
    i = 0
    elements = []

    def __init__(self, elements: list):
        self.elements = elements

    def next_job(self):
        self.i = (self.i + 1) % len(self.elements)
        return self.elements[self.i-1]

    def complete_job(self, replacer):
        self.elements[self.i] = replacer


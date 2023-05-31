class StatsGroup:
    def __init__(self):
        self.stats = {}
    def addStat(self, name, initial_value):
        self.stats[name] = initial_value

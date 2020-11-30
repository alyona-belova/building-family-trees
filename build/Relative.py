class Relative:
    def __init__(self, id, name, color):
        self.id = id
        self.name = name  # русскоязычное название термина родства
        self.color = color  # {0; 1; -1} - каким цветом будет нарисован

        # заполнение шести возможных прямых связей: список id тех, с кем эта связь
        self.relations = {'mother': [], 'father': [], 'daughter': [], 'son': [], 'husband': [], 'wife': []}

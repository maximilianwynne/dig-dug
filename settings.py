import pygame

class Settings():
    def __init__(self):
        self.bg_colour = (0,0,0)

# player settings
    player_measure = 23.3
    player_speed = 1.2345
    player_height = player_measure
    player_width = player_measure

# ground settings
    cell_measure = 19.5
    cell_colour = (255,0,0)

# monster settings
    monster_colour = (214, 23, 166)

# scoreboard
    board_bg_colour = (0, 0, 0)
    board_font_colour = (244, 244, 244)
import pygame
import pygame.font as font

class Dashboard():
    def __init__(self,screen,settings,game_stats):
        self.screen = screen
        self.settings = settings
        self.screen_rect = self.screen.get_rect()
        self.game_stats = game_stats
        self.score_font = font.Font(30)
        self.hs_font = font.Font(35)

        self.board_surface = pygame.Surface((self.screen_rect.WIDTH, 100))
        self.board_surface.fill(self.settings.bg_colour)
        self.board_rect = self.board_surface.get_rect()
        self.board_rect.x = ((self.screen_rect.WIDTH - self.board_surface.get_rect().width)) / 2
        self.board_rect.y = 0

        self.title_high_score()
        self.prep_high_score()
        self.prep_score()

def __blit__(self):
    self.screen.blit(self.board_surface,self.board_rect)
    self.board_surface.blit(self.score_img,self.score_rect)
    self.board_surface.blit(self.high_score_img,self.high_rect)
    self.board_surface.blit(self.title,self.title_high_score_rect)

def title_high_score(self):
    title_high_score_str = str("High Score")
    title_high_score_str = self.hs_font.render(title_high_score_str, True)
    self.title_high_score_rect.x = ((self.screen_rect.WIDTH - self.title.high_score_rect.WIDTH)) / 2




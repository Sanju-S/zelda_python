import pygame

from settings import *
from player import Player

class Upgrade:
    def __init__(self, player: Player) -> None:
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.attribute_nr = len(player.stats)
        self.attribute_names = list(player.stats.keys())
        self.max_values = list(player.max_stats.values())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # item creation
        self.height = self.display_surface.get_size()[1] * 0.8
        self.width = self.display_surface.get_size()[0] // 6
        self.create_items()

        # selection system
        self.selection_index = 0
        self.selection_time = 0
        self.can_move = True
        self.selection_cool_time = 300
    
    def input(self) -> None:
        keys = pygame.key.get_pressed()

        if self.can_move:
            if keys[pygame.K_RIGHT] and self.selection_index < self.attribute_nr - 1:
                self.selection_index += 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            elif keys[pygame.K_LEFT] and self.selection_index >= 1:
                self.selection_index -= 1
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
            
            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.selection_time = pygame.time.get_ticks()
                self.item_list[self.selection_index].trigger(self.player)
    
    def selection_cooldown(self) -> None:
        if not self.can_move:
            current_time = pygame.time.get_ticks()
            if (current_time - self.selection_time) >= self.selection_cool_time:
                self.can_move = True

    def create_items(self) -> None:
        self.item_list: list[Item] = []

        for index, item in enumerate(range(self.attribute_nr)):
            # horizontal position
            full_width = self.display_surface.get_size()[0]
            increment = full_width // self.attribute_nr
            left = (item * increment) + (increment - self.width) // 2

            # vertical position
            top = self.display_surface.get_size()[1] * 0.1

            # create the object
            item = Item(left, top, self.width, self.height, index, self.font, self.player)
            self.item_list.append(item)

    def display(self) -> None:
        self.input()
        self.selection_cooldown()

        for index, item in enumerate(self.item_list):
            # get attributes
            name = self.attribute_names[index]
            value = self.player.get_value_by_index(index)
            max_value = self.max_values[index]
            cost = self.player.get_cost_by_index(index)
            item.display(self.display_surface, self.selection_index, name, value, max_value, cost)


class Item:
    def __init__(self, left: float, top: float, width: float, height: float, index: int, font: pygame.font.Font, player: Player) -> None:
        self.rect = pygame.Rect(left, top, width, height)
        self.index = index
        self.font = font
        self.player = player
    
    def display_names(self, surface: pygame.Surface, name: str, cost: int, selected: bool) -> None:
        color = TEXT_COLOR_SELCTED if selected else TEXT_COLOR

        # title
        title_surface = self.font.render(name, False, color)
        title_rect = title_surface.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 20))

        # cost
        upgrade_attr = list(self.player.stats.keys())[self.index]
        if self.player.stats[upgrade_attr] >= self.player.max_stats[upgrade_attr]:
            cost_surface = self.font.render('MAX', False, color)
        else:
            cost_surface = self.font.render(f'{int(cost)}', False, color)
        cost_rect = cost_surface.get_rect(midbottom=self.rect.midbottom - pygame.math.Vector2(0, 20))

        # draw
        surface.blit(title_surface, title_rect)
        surface.blit(cost_surface, cost_rect)
    
    def display_bar(self, surface: pygame.Surface, value: int, max_value: int, selected: bool) -> None:
        # drawing setup
        top = self.rect.midtop + pygame.math.Vector2(0, 60)
        bottom = self.rect.midbottom - pygame.math.Vector2(0, 60)
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR

        # bar setup
        full_height = bottom[1] - top[1]
        relative_number = (value / max_value) * full_height
        value_rect = pygame.Rect(top[0] - 15, bottom[1] - relative_number, 30, 10)

        # draw elements
        LINE_WIDTH = 5
        pygame.draw.line(surface, color, top, bottom, LINE_WIDTH)
        pygame.draw.rect(surface, color, value_rect)
    
    def trigger(self, player: Player) -> None:
        upgrade_attr = list(player.stats.keys())[self.index]

        if player.exp >= player.upgrade_cost[upgrade_attr] and player.stats[upgrade_attr] < player.max_stats[upgrade_attr]:
            player.exp -= player.upgrade_cost[upgrade_attr]
            player.stats[upgrade_attr] *= 1.2
            player.upgrade_cost[upgrade_attr] *= 1.4
        
        if player.stats[upgrade_attr] > player.max_stats[upgrade_attr]:
            player.stats[upgrade_attr] = player.max_stats[upgrade_attr]
    
    def display(self, surface: pygame.Surface, selection_num: int, name: str, value: int, max_value: int, cost: int) -> None:
        if self.index == selection_num:
            pygame.draw.rect(surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        self.display_names(surface, name, cost, self.index == selection_num)
        self.display_bar(surface, value, max_value, self.index == selection_num)


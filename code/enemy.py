import pygame

from settings import *
from entity import Entity
from support import *
from player import Player

class Enemy(Entity):
    def __init__(self, monster_name: str, pos: tuple[int], groups: list[pygame.sprite.Group], obstacle_sprites: pygame.sprite.Group, damage_player, trigger_death_particles, add_xp) -> None:
        # general setup
        super().__init__(groups)
        self.sprite_type = 'enemy'

        # graphics setup
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image: pygame.Surface = self.animations[self.status][self.frame_index]

        # movement
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites

        # stats
        self.monster_name = monster_name
        monster_info: dict[str, int] = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']

        # player interaction
        self.can_attack = True
        self.attack_time = 0
        self.attack_cooldown = 400
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_xp = add_xp

        # invincibility time
        self.vulnerable = True
        self.hit_time = 0
        self.invincibility_duration = 300

        # sounds
        self.death_sound = pygame.mixer.Sound('../audio/death.wav')
        self.hit_sound = pygame.mixer.Sound('../audio/hit.wav')
        self.attack_sound = pygame.mixer.Sound(monster_info['attack_sound'])
        self.death_sound.set_volume(0.2)
        self.hit_sound.set_volume(0.2)
        self.attack_sound.set_volume(0.2)
    
    def import_graphics(self, monster_name: str) -> None:
        self.animations = {'idle': [], 'move': [], 'attack':[]}
        main_path = f'../graphics/monsters/{monster_name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def get_player_distance_direction(self, player: Player) -> dict[str: float | pygame.math.Vector2]:
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2(0, 0)

        return {
            'distance': distance,
            'direction': direction
        }
    
    def get_status(self, player: Player) -> None:
        distance: float = self.get_player_distance_direction(player)['distance']

        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'
    
    def actions(self, player: Player) -> None:
        if self.status == 'attack':
            self.attack_sound.play()
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_damage, self.attack_type)
        elif self.status == 'move':
            self.direction: pygame.math.Vector2 = self.get_player_distance_direction(player)['direction']
        else:
            self.direction = pygame.math.Vector2()
    
    def animate(self) -> None:
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0
        
        self.image: pygame.Surface = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)
        
    def cooldowns(self) -> None:
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if (current_time - self.attack_time) >= self.attack_cooldown:
                self.can_attack = True
        
        if not self.vulnerable:
            if (current_time - self.hit_time) >= self.invincibility_duration:
                self.vulnerable = True

    def get_damage(self, player: Player, attack_type: str) -> None:
        if self.vulnerable:
            self.hit_sound.play()
            self.direction = self.get_player_distance_direction(player)['direction']
            if attack_type == 'weapon':
                self.health -= player.get_full_weapon_damage()
            else:
                self.health -= player.get_full_magic_damage()
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False
    
    def check_death(self) -> None:
        if self.health <= 0:
            self.death_sound.play()
            self.kill()
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.add_xp(self.exp)

    def hit_reaction(self) -> None:
        if not self.vulnerable:
            self.direction *= -self.resistance

    def update(self) -> None:
        self.hit_reaction()
        self.move(self.speed)
        self.animate()
        self.cooldowns()
        self.check_death()
    
    def enemy_update(self, player: Player) -> None:
        self.get_status(player)
        self.actions(player)


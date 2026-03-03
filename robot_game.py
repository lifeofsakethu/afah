import pygame
import random
import math
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
CLOCK = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    WIN = 4

class Robot(pygame.sprite.Sprite):
    def __init__(self, x, y, color=BLUE):
        super().__init__()
        self.color = color
        self.size = 15
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.draw_robot(self.image)
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)
        self.vx = 0
        self.vy = 0
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.armor = 0
        self.weapon_cooldown = 0
        self.angle = 0

    def draw_robot(self, surface):
        pygame.draw.circle(surface, self.color, (self.size, self.size), self.size)
        pygame.draw.circle(surface, WHITE, (self.size, self.size), self.size, 2)
        pygame.draw.circle(surface, YELLOW, (self.size + 8, self.size - 5), 3)

    def draw_health_bar(self, surface):
        bar_width = 40
        bar_height = 5
        bar_x = self.rect.x
        bar_y = self.rect.y - 10
        
        pygame.draw.rect(surface, RED, (bar_x, bar_y, bar_width, bar_height))
        health_percent = max(0, self.health / self.max_health)
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, bar_width * health_percent, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def update(self, keys=None):
        if keys:
            self.vx = 0
            self.vy = 0
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.vy = -self.speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.vy = self.speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.vx = -self.speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.vx = self.speed

        self.x += self.vx
        self.y += self.vy
        
        # Screen boundaries
        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))
        
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        if self.weapon_cooldown > 0:
            self.weapon_cooldown -= 1

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.armor)
        self.health -= actual_damage
        return self.health <= 0

    def is_alive(self):
        return self.health > 0

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, color=YELLOW):
        super().__init__()
        self.color = color
        self.image = pygame.Surface((6, 6))
        pygame.draw.circle(self.image, color, (3, 3), 3)
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.speed = 8

    def update(self):
        self.x += self.vx * self.speed
        self.y += self.vy * self.speed
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        if (self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or 
            self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT):
            self.kill()

class Enemy(Robot):
    def __init__(self, x, y):
        super().__init__(x, y, color=RED)
        self.max_health = 50
        self.health = self.max_health
        self.speed = 2
        self.attack_cooldown = 0
        self.behavior_change_timer = 0

    def update(self, player_pos):
        self.attack_cooldown = max(0, self.attack_cooldown - 1)
        self.behavior_change_timer += 1
        
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 30:
            if distance > 0:
                self.vx = (dx / distance) * self.speed
                self.vy = (dy / distance) * self.speed
            else:
                self.vx = 0
                self.vy = 0
        else:
            self.vx = 0
            self.vy = 0
        
        self.x += self.vx
        self.y += self.vy
        
        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))
        
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

    def fire_at_player(self, player_pos):
        if self.attack_cooldown <= 0:
            dx = player_pos[0] - self.x
            dy = player_pos[1] - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                bullet_vx = dx / distance
                bullet_vy = dy / distance
                
                self.attack_cooldown = 30
                return Bullet(self.x, self.y, bullet_vx, bullet_vy, color=ORANGE)
        return None

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ROBOT BATTLEGROUND")
        self.state = GameState.MENU
        self.reset_game()

    def reset_game(self):
        self.player = Robot(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, color=BLUE)
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.wave = 1
        self.score = 0
        self.kills = 0
        self.spawn_wave()

    def spawn_wave(self):
        num_enemies = min(2 + self.wave, 8)
        for _ in range(num_enemies):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            if math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2) > 100:
                self.enemies.add(Enemy(x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU and event.key == pygame.K_SPACE:
                    self.state = GameState.PLAYING
                elif self.state == GameState.GAME_OVER and event.key == pygame.K_SPACE:
                    self.reset_game()
                    self.state = GameState.PLAYING
                elif self.state == GameState.WIN and event.key == pygame.K_SPACE:
                    self.reset_game()
                    self.state = GameState.PLAYING
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
            if event.type == pygame.MOUSEBUTTONDOWN and self.state == GameState.PLAYING:
                self.player_shoot()
        return True

    def player_shoot(self):
        if self.player.weapon_cooldown <= 0:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - self.player.x
            dy = mouse_y - self.player.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                bullet_vx = dx / distance
                bullet_vy = dy / distance
                self.player_bullets.add(Bullet(self.player.x, self.player.y, bullet_vx, bullet_vy, color=CYAN))
                self.player.weapon_cooldown = 15

    def update(self):
        if self.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            self.player.update(keys)
            
            for enemy in self.enemies:
                enemy.update(self.player.rect.center)
                bullet = enemy.fire_at_player(self.player.rect.center)
                if bullet:
                    self.enemy_bullets.add(bullet)
            
            self.player_bullets.update()
            self.enemy_bullets.update()
            
            # Check bullet-enemy collisions
            for bullet in self.player_bullets:
                hit_enemies = pygame.sprite.spritecollide(bullet, self.enemies, False)
                if hit_enemies:
                    for enemy in hit_enemies:
                        if enemy.take_damage(25):
                            self.kills += 1
                            self.score += 100
                            enemy.kill()
                    bullet.kill()
            
            # Check bullet-player collisions
            for bullet in self.enemy_bullets:
                if pygame.sprite.spritecollide(bullet, pygame.sprite.Group(self.player), False):
                    if self.player.take_damage(10):
                        self.state = GameState.GAME_OVER
                    bullet.kill()
            
            # Check enemy-player collisions
            for enemy in self.enemies:
                if pygame.sprite.spritecollide(enemy, pygame.sprite.Group(self.player), False):
                    if self.player.take_damage(5):
                        self.state = GameState.GAME_OVER
            
            # Wave management
            if len(self.enemies) == 0:
                self.wave += 1
                if self.wave > 5:
                    self.state = GameState.WIN
                else:
                    self.spawn_wave()
                    self.score += 500

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.WIN:
            self.draw_win()
        
        pygame.display.flip()

    def draw_menu(self):
        font_large = pygame.font.Font(None, 60)
        font_medium = pygame.font.Font(None, 40)
        font_small = pygame.font.Font(None, 24)
        
        title = font_large.render("ROBOT BATTLEGROUND", True, CYAN)
        self.screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 100))
        
        subtitle = font_medium.render("Click to shoot", True, GREEN)
        self.screen.blit(subtitle, ((SCREEN_WIDTH - subtitle.get_width()) // 2, 200))
        
        instructions = [
            "WASD or Arrow Keys to move",
            "MOUSE CLICK to shoot",
            "Destroy all enemies to advance",
            "5 waves to victory!",
            "",
            "Press SPACE to start"
        ]
        
        y_offset = 300
        for instruction in instructions:
            text = font_small.render(instruction, True, WHITE)
            self.screen.blit(text, ((SCREEN_WIDTH - text.get_width()) // 2, y_offset))
            y_offset += 35

    def draw_game(self):
        # Draw sprites
        self.player_bullets.draw(self.screen)
        self.enemy_bullets.draw(self.screen)
        self.enemies.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)
        
        # Draw health bars
        self.player.draw_health_bar(self.screen)
        for enemy in self.enemies:
            enemy.draw_health_bar(self.screen)
        
        # Draw UI
        font = pygame.font.Font(None, 30)
        wave_text = font.render(f"Wave: {self.wave}/5", True, CYAN)
        score_text = font.render(f"Score: {self.score}", True, GREEN)
        health_text = font.render(f"Health: {max(0, int(self.player.health))}", True, RED)
        kills_text = font.render(f"Kills: {self.kills}", True, YELLOW)
        
        self.screen.blit(wave_text, (10, 10))
        self.screen.blit(score_text, (10, 50))
        self.screen.blit(health_text, (SCREEN_WIDTH - health_text.get_width() - 10, 10))
        self.screen.blit(kills_text, (SCREEN_WIDTH - kills_text.get_width() - 10, 50))

    def draw_game_over(self):
        font_large = pygame.font.Font(None, 80)
        font_medium = pygame.font.Font(None, 40)
        font_small = pygame.font.Font(None, 30)
        
        game_over = font_large.render("GAME OVER", True, RED)
        self.screen.blit(game_over, ((SCREEN_WIDTH - game_over.get_width()) // 2, 150))
        
        score_text = font_medium.render(f"Final Score: {self.score}", True, YELLOW)
        self.screen.blit(score_text, ((SCREEN_WIDTH - score_text.get_width()) // 2, 280))
        
        kill_text = font_medium.render(f"Enemies Destroyed: {self.kills}", True, YELLOW)
        self.screen.blit(kill_text, ((SCREEN_WIDTH - kill_text.get_width()) // 2, 340))
        
        restart = font_small.render("Press SPACE to retry", True, CYAN)
        self.screen.blit(restart, ((SCREEN_WIDTH - restart.get_width()) // 2, 450))
        
        menu = font_small.render("Press ESC for menu", True, WHITE)
        self.screen.blit(menu, ((SCREEN_WIDTH - menu.get_width()) // 2, 500))

    def draw_win(self):
        font_large = pygame.font.Font(None, 80)
        font_medium = pygame.font.Font(None, 40)
        font_small = pygame.font.Font(None, 30)
        
        victory = font_large.render("VICTORY!", True, GREEN)
        self.screen.blit(victory, ((SCREEN_WIDTH - victory.get_width()) // 2, 150))
        
        score_text = font_medium.render(f"Final Score: {self.score}", True, YELLOW)
        self.screen.blit(score_text, ((SCREEN_WIDTH - score_text.get_width()) // 2, 280))
        
        kill_text = font_medium.render(f"Enemies Destroyed: {self.kills}", True, YELLOW)
        self.screen.blit(kill_text, ((SCREEN_WIDTH - kill_text.get_width()) // 2, 340))
        
        restart = font_small.render("Press SPACE for next round", True, CYAN)
        self.screen.blit(restart, ((SCREEN_WIDTH - restart.get_width()) // 2, 450))
        
        menu = font_small.render("Press ESC for menu", True, WHITE)
        self.screen.blit(menu, ((SCREEN_WIDTH - menu.get_width()) // 2, 500))

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            CLOCK.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

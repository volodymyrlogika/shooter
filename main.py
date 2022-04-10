import os
import sys
from random import randint

import pygame

# Ми завантажуємо окремо функції для роботи з шрифтом
pygame.init()
pygame.font.init()
font1 = pygame.font.SysFont("Arial", 80)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))

font2 = pygame.font.SysFont("Arial", 36)


#фонова музика
pygame.mixer.init()

dirn = os.path.dirname(sys.argv[0])

pygame.mixer.music.load(os.path.join(dirn, 'assets/sounds/space.ogg'))
pygame.mixer.music.play()
fire_sound = pygame.mixer.Sound(os.path.join(dirn, 'assets/sounds/fire.ogg'))

# Нам потрібні такі фотографії:
img_back = os.path.join(dirn, "assets/pics/space_bg.jpg") # фон игры
 
img_bullet = os.path.join(dirn, "assets/pics/bullet.png") # пуля
img_hero = os.path.join(dirn, "assets/pics/spaceship.png") # герой
img_enemy = os.path.join(dirn, "assets/pics/ufo.png") # ворог
 
score = 0 # Збито корбалів
goal = 10 # скільки кораблів потрібно збити для перемоги
lost = 0 # Пропущені кораблі
max_lost = 3 
 
# Батьківський клас для інших спрайтів
class GameSprite(pygame.sprite.Sprite):
  # конструктор класса
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        # Викликаємо конструктор класу (Sprite):
        pygame.sprite.Sprite.__init__(self)

        #Кожен спрайт повинен зберігати властивість image - зображення
        self.image = pygame.transform.scale(pygame.image.load(player_image), (size_x, size_y))
        self.speed = player_speed

        # Кожен спрайт повинен зберігати властивість rect - прямокутник, в якому він увійшов
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
 
  # Метод, що малює спрайт у вікні
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# Клас головного гравця
class Player(GameSprite):
    # Спосіб управління спрайтом стрілками клавіатури
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
  # Метод "постріл" (ми використовуємо позицію гравця, щоб створити кулю там)
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

# клас спрайта ворога
class Enemy(GameSprite):
    # Рух ворога
    def update(self):
        self.rect.y += self.speed
        global lost
        # зникає, якщо доходить до краю екрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost = lost + 1
 
# клас спрайта кулі
class Bullet(GameSprite):
    # Рух ворога
    def update(self):
        self.rect.y += self.speed
        # зникає, якщо доходить до краю екрана
        if self.rect.y < 0:
            self.kill()
 
# Створити вікно
win_width = 700
win_height = 500
pygame.display.set_caption("Шутер")
window = pygame.display.set_mode((win_width, win_height))
background = pygame.transform.scale(pygame.image.load(img_back), (win_width, win_height))
 
# Створюємо спрайти
ship = Player(img_hero, 5, win_height - 140, 60, 100, 10)

# Створення групи спрайтів-ворогів
monsters = pygame.sprite.Group()
for i in range(1, 6):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
    monsters.add(monster)
 
bullets = pygame.sprite.Group()
 
# Змінна "Гра закінчилася": як тільки вона стане True, спрайти припиняють працювати в основному циклі
finish = False
# Основний цикл гри:
run = True # Прапор скидається кнопку закриття вікна
while run:
    # Закриття кнопки закриття
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False
        # Подія натискання на пробіл - спрайт стріляє
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                fire_sound.play()
                ship.fire()
 
  # Сама гра: дії спрайтів, перевірка правил гри, переписовка
    if not finish:
        # оновлюємо фон
        window.blit(background,(0,0))

        # пишемо текст на екрані
        text = font2.render("Рахунок: " + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))

        text_lose = font2.render("Пропущено: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))

        # запускаємо рух спрайтів
        ship.update()
        monsters.update()
        bullets.update()

        # оновлюємо спрайти у новому місці на кожній ітерації циклу
        ship.reset()
        monsters.draw(window)
        bullets.draw(window)
 
        # Перевірка зіткнення куль і монстрів (і монстр, і кулі при зіткненні зникають)
        collides = pygame.sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            # Цей цикл повториться стільки разів, скільки монстрів підбито
            score = score + 1
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        # Можливий програш: пропустили занадто багато, або герой зіткнувся з ворогом
        if pygame.sprite.spritecollide(ship, monsters, False) or lost >= max_lost:
            finish = True # Програли, намалювали фон і більше не керуємо спрайтами.
            window.blit(lose, (200, 200))

        # Перевірка виграшу: скільки балів зароблено
        if score >= goal:
            finish = True
            window.blit(win, (200, 200))

        pygame.display.update()
    # цикл спрацьовує кожні 0,05 секунди
    pygame.time.delay(50)
input()
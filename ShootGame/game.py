# -*- coding: utf-8 -*-
import pygame
from sys import exit
from pygame.locals import *
import random
from random import randrange, choice


SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800
vita=6
#生命数

#定义玩家、敌机类     -----------------------------------------------------------------------------
class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_img, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        #得到一个矩阵
        self.rect.midbottom = init_pos
        self.speed = 10

    def move(self):

        self.rect.top -= self.speed
       


class Player(pygame.sprite.Sprite):
    def __init__(self, plane_img, player_rect, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = []                             
        for i in range(len(player_rect)):
            self.image.append(plane_img.subsurface(player_rect[i]).convert_alpha())
        #添加所有飞机型号
        self.rect = player_rect[0]                   
        self.rect.topleft = init_pos              
        self.speed = 8                             
        self.bullets = pygame.sprite.Group()            
        self.img_index = 0    
        #决定飞机型号                         
        self.is_hit = False                             

    def shoot(self, bullet_img):
        for i in range(level+1):
            bullet = Bullet(bullet_img,[self.rect.midtop[0]+20*i,self.rect.midtop[1]])            
            self.bullets.add(bullet)
            bullet = Bullet(bullet_img,[self.rect.midtop[0]-20*i,self.rect.midtop[1]])
            self.bullets.add(bullet)

    def moveUp(self):
        if self.rect.top <= 0:
            self.rect.top = 0
        else:
            self.rect.top -= self.speed


    def moveDown(self):
        if self.rect.top >= SCREEN_HEIGHT - self.rect.height:
            self.rect.top = SCREEN_HEIGHT - self.rect.height
        else:
            self.rect.top += self.speed


    def moveLeft(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        else:
            self.rect.left -= self.speed

      
    def moveRight(self):
        if self.rect.left >= SCREEN_WIDTH - self.rect.width:
            self.rect.left = SCREEN_WIDTH - self.rect.width
        else:
            self.rect.left += self.speed

class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_img, enemy_down_imgs, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.topleft = init_pos
        self.down_imgs = enemy_down_imgs
        self.speed = 2
        self.down_index = 0

    def shoot(self, bullet_img):
        bullet = EnBullet(bullet_img,self.rect.midbottom)
        Enemybullets.add(bullet)
    def move(self):
        self.rect.top += self.speed

class boss(pygame.sprite.Sprite):
    def __init__(self, enemy_img, enemy_down_imgs, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.bottomleft = init_pos

        self.down_imgs = enemy_down_imgs
        self.speed = randrange(1)
        self.down_index = 0
        self.life=500
        self.time=0
        if self.rect.left<SCREEN_WIDTH/2:
            self.goleft= False
        else:
            self.goleft=True
    def shoot(self, bullet_img):
        for i in range(randrange(5)):
            bullet = BossBullet(bullet_img,[self.rect.midbottom[0]+20*i,self.rect.midbottom[1]])            
            Enemybullets.add(bullet)
            bullet = BossBullet(bullet_img,[self.rect.midbottom[0]-20*i,self.rect.midbottom[1]])
            Enemybullets.add(bullet)
    def move(self):
        if self.rect.right>SCREEN_WIDTH:
            self.goleft=True
        if self.rect.left<0:
            self.goleft=False

        if self.goleft:
            self.rect.left -=  self.speed
        else:
            self.rect.left += self.speed
        if  (self.rect.top<0 and self.time>9):
            self.rect.top+=1
        self.time+=1
        if self.time>10:
            self.time=0


class EnBullet(pygame.sprite.Sprite):
    def __init__(self, bullet_img, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        #得到一个矩阵
        self.rect.midbottom = init_pos
        self.speed = 4
        self.choicespeed=randrange(-4,4)

    def move(self):
        
        self.rect.top += self.speed
        self.rect.left+=self.choicespeed


class BossBullet(pygame.sprite.Sprite):
    def __init__(self, bullet_img, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        #得到一个矩阵
        self.rect.midbottom = init_pos
        self.speed = 5
        self.choicespeed=randrange(-8,8)

    def move(self):
        
        self.rect.top += self.speed
        self.rect.left+=self.choicespeed

#定义玩家、敌机类     --------------------------------------------------------------------------------------------------------------------------------

#初始化游戏，设置参数      -------------------------------------------------------------------------------------------------------------------------
pygame.init()


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


pygame.display.set_caption('灰机大战')

background = pygame.image.load('resources/image/background.png').convert()

game_over = pygame.image.load('resources/image/gameover.png')


plane_img = pygame.image.load('resources/image/shoot.png')


player_rect = []
player_rect.append(pygame.Rect(0, 99, 102, 126))        
player_rect.append(pygame.Rect(165, 360, 102, 126))
player_rect.append(pygame.Rect(165, 234, 102, 126))    
player_rect.append(pygame.Rect(330, 624, 102, 126))
player_rect.append(pygame.Rect(330, 498, 102, 126))
player_rect.append(pygame.Rect(432, 624, 102, 126))
player_pos = [200, 600]
player = Player(plane_img, player_rect, player_pos)


bullet_rect = pygame.Rect(1004, 987, 9, 21)
#像素位置
bullet_img = plane_img.subsurface(bullet_rect)
#截取某图片

enemy1_rect = pygame.Rect(534, 612, 57, 43)
enemy1_img = plane_img.subsurface(enemy1_rect)
enemy2_rect=pygame.Rect(163,753,165,239)
enemy2_img = plane_img.subsurface(enemy2_rect)
enemy1_down_imgs = []
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(267, 347, 57, 43)))
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(873, 697, 57, 43)))
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(267, 296, 57, 43)))
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(930, 697, 57, 43)))

enemy2_down_imgs=[]
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(3, 487, 164, 238)))
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(3, 227, 165, 237)))
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(841, 750, 162, 238)))
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(166, 488, 162, 246)))
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(673, 750, 165, 249)))
enemy1_down_imgs.append(plane_img.subsurface(pygame.Rect(0, 760, 149, 199)))

#不同的boss

enemies1 = pygame.sprite.Group()
#生成的敌机
Enemybullets=pygame.sprite.Group()
enemies_down = pygame.sprite.Group()
boss_down = pygame.sprite.Group()
enemies2=pygame.sprite.Group()
#消灭的敌机

shoot_frequency = 0
enemy_frequency = 0
enshoot_frequency = 0
boss_frequency=1
boss_shoot=0

player_down_index = 16


score = 0
level=0
clock = pygame.time.Clock()

#初始化游戏，设置参数      -------------------------------------------------------------------------------------------------------------------------
running = True


while running:
 
    clock.tick(60)

    
#控制生成敌机、boss、子弹的频率  -------------------------------------  -----------------------------------------------------
    if not player.is_hit:
        if shoot_frequency % (15-2*level) == 0:
            player.shoot(bullet_img)
        shoot_frequency += 1
        if shoot_frequency >= (15-2*level):
            shoot_frequency = 0


    if enemy_frequency % (50-10*level)== 0:
        enemy1_pos = [random.randint(0, SCREEN_WIDTH - enemy1_rect.width), 0]
        enemy1 = Enemy(enemy1_img, enemy1_down_imgs, enemy1_pos)
        enemies1.add(enemy1)
        

    enemy_frequency += 1
    if enemy_frequency >= (50-10*level):
        enemy_frequency = 0

    if boss_frequency % (1000-10*level)== 0:
        enemy2_pos = [random.randint(0, SCREEN_WIDTH - enemy2_rect.width), 0]
        enemy2 = boss(enemy2_img, enemy1_down_imgs, enemy2_pos)
        enemies2.add(enemy2)
    boss_frequency+=1
    if boss_frequency >= (1000-10*level):
        boss_frequency=0

    
    if enshoot_frequency % (250-10*level)== 0:
        for i in enemies1:
            i.shoot(bullet_img)
    enshoot_frequency+=1


    if enshoot_frequency >= (250-10*level):
        enshoot_frequency=0


    if boss_shoot % (100-10*level)== 0:
        try:
            for i in enemies2:
                i.shoot(bullet_img)
        except Exception:
            pass

    boss_shoot+=1
    if boss_shoot >= (100-10*level):
        boss_shoot=0
#控制生成敌机、boss、子弹的频率  ------------------------------------------------------------------------------------------------------


#触发事件，如果相撞   -------------------------------------------------------------------------------------------------------

    for enbullet in Enemybullets:
        enbullet.move()

        if enbullet.rect.bottom < 0:
            Enemybullets.remove(enbullet)

        if pygame.sprite.collide_circle(enbullet, player):
            Enemybullets.remove(enbullet)
            player.is_hit = True
        


    for bullet in player.bullets:
  
        bullet.move()
     
        if bullet.rect.bottom < 0:
            player.bullets.remove(bullet)   

    for enemy in enemies1:
      
        enemy.move()
 
        if pygame.sprite.collide_circle(enemy, player):
            enemies_down.add(enemy)
            #消灭的飞机
            enemies1.remove(enemy)
            #移除敌机
            player.is_hit = True
            break

        if enemy.rect.top < 0:
            enemies1.remove(enemy)
        


    enemies1_down = pygame.sprite.groupcollide(enemies1, player.bullets, 1, 1)
   #子弹与敌机碰撞


    for enemy_down in enemies1_down:
        enemies_down.add(enemy_down)

    for bulletss in player.bullets:
        for bosses in enemies2:
            bosses.move()
            if pygame.sprite.collide_circle(bulletss, bosses):
                bosses.life-=1
                player.bullets.remove(bulletss)
 
                if bosses.life<=0:
                    boss_down.add(bosses)
                    enemies2.remove(bosses)    
#触发事件，如果相撞   ----------------------------------------------------------------------------
    screen.fill(0)
    screen.blit(background, (0, 0))


#屏幕加入背景

#如果玩家死亡  ------------------------------------------------
    if not player.is_hit:
        screen.blit(player.image[level], player.rect)

    else:

        player.img_index = player_down_index / 8
        screen.blit(player.image[level], player.rect)
        #失败时的图
        #失败后需循环47次
        player_down_index += 1
        player.is_hit = False 
        vita-=1
        if vita == 0:        
        #player_down_index=16 有4条命

            running = False
        
#如果玩家死亡  ------------------------------------------------
    for enemy_down in enemies_down:
        if enemy_down.down_index == 0:
            pass
    #循环七次才执行消灭，画出消灭图
        if enemy_down.down_index > 7:
            enemies_down.remove(enemy_down)
            score += 1000
            continue
        if score <= 42000:
            level=score/10000
        
        
        screen.blit(enemy_down.down_imgs[enemy_down.down_index / 7], enemy_down.rect)
        #加入渐变效果，连续七次不一样的图片组合出消灭的特效
        enemy_down.down_index += 1

    for bosses_down in boss_down:
        if bosses_down.down_index == 0:
            pass
    #循环七次才执行消灭，画出消灭图
        if bosses_down.down_index > 20:
            boss_down.remove(bosses_down)
            score += 5000
            continue        
        
        screen.blit(bosses_down.down_imgs[bosses_down.down_index / 4], bosses_down.rect)
        #加入渐变效果，连续七次不一样的图片组合出消灭的特效
        bosses_down.down_index += 1
 


    player.bullets.draw(screen)
    Enemybullets.draw(screen)
    enemies2.draw(screen)
    enemies1.draw(screen)
    #画出子弹和敌机

#屏幕显示生命数   -----------------------------------------------------------------
    score_font = pygame.font.Font(None, 36)
    score_text = score_font.render('score:'+str(score), True, (128, 128, 128))
    text_rect = score_text.get_rect()
    text_rect.topleft = [10, 10]
    screen.blit(score_text, text_rect)
 
    level_font = pygame.font.Font(None, 36)
    level_text = score_font.render('level:'+str(level), True, (128, 128, 128))
    text_rect1 = score_text.get_rect()
    text_rect1.topleft = [400, 10]
    screen.blit(level_text, text_rect1)

    vita_font = pygame.font.Font(None, 36)
    vita_text = score_font.render('vita:'+str(vita), True, (128, 128, 128))
    text_rect2 = score_text.get_rect()
    text_rect2.topleft = [200, 10]
    screen.blit(vita_text, text_rect2)
#屏幕显示生命数   -----------------------------------------------------------------

    pygame.display.update()
    #更新屏幕
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
#键盘输入       ----------------------------------------------------------------            
    key_pressed = pygame.key.get_pressed()

    if key_pressed[K_w] or key_pressed[K_UP]:
        player.moveUp()
    if key_pressed[K_s] or key_pressed[K_DOWN]:
        player.moveDown()
    if key_pressed[K_a] or key_pressed[K_LEFT]:
        player.moveLeft()
    if key_pressed[K_d] or key_pressed[K_RIGHT]:
        player.moveRight()
#键盘输入       ----------------------------------------------------------------


font = pygame.font.Font(None, 48)
text = font.render('Score: '+ str(score), True, (255, 0, 0))
text_rect = text.get_rect()
text_rect.centerx = screen.get_rect().centerx
text_rect.centery = screen.get_rect().centery + 24
screen.blit(game_over, (0, 0))
screen.blit(text, text_rect)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    pygame.display.update()

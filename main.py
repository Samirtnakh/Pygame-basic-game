import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

sayac = pygame.time.Clock()
fps = 60

ekran_gen = 1000
ekran_yuk = 1000

ekran = pygame.display.set_mode((ekran_gen, ekran_yuk))
pygame.display.set_caption('Minecraft Platform')

font = pygame.font.SysFont('Bauhaus 93', 70)
skor_font = pygame.font.SysFont('Bauhaus 93', 30)


kareBoyutu = 50
oyunBittimi = 0
anaMenu = True
seviyeIndex = 7
tumSeviyeler = 7
score = 0

beyaz = (255, 255, 255)
mavi = (0, 0, 255)

gunesAsset = pygame.image.load('resim/gunes.png')
bgAsset = pygame.image.load('resim/gokyuzu.png')
tekrarAsset = pygame.image.load('resim/restartbtn.png')
baslatAsset = pygame.image.load('resim/startbtn.png')
cikisAsset = pygame.image.load('resim/cikisbtn.png')

pygame.mixer.music.load('resim/muzik.mp3')
pygame.mixer.music.play(-1, 0.0, 5000)
altinSes = pygame.mixer.Sound('resim/elmas.wav')
altinSes.set_volume(0.5)
ziplamaSes = pygame.mixer.Sound('resim/zipla.wav')
ziplamaSes.set_volume(0.5)
oyunBittiSes = pygame.mixer.Sound('resim/oyunbitti.mp3')
oyunBittiSes.set_volume(0.5)


def metinYazdir(metin, font, metinBoyutu, x, y):
    resim = font.render(metin, True, metinBoyutu)
    ekran.blit(resim, (x, y))


def seviyeyiSifirla(seviyeIndex):
    oyuncu.reset(100, ekran_yuk - 130)
    yaratiklar.empty()
    platformlar.empty()
    altinlar.empty()
    lavlar.empty()
    cikislar.empty()

    if path.exists(f'seviye{seviyeIndex}_data'):
        pickle_yukleyici = open(f'seviye{seviyeIndex}_data', 'rb')
        seviyeBilgisi = pickle.load(pickle_yukleyici)
    seviye = World(seviyeBilgisi)
    altinSkoru = Altin(kareBoyutu // 2, kareBoyutu // 2)
    altinlar.add(altinSkoru)
    return seviye


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.tiklandi = False

    def draw(self):
        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.tiklandi == False:
                action = True
                self.tiklandi = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.tiklandi = False


        ekran.blit(self.image, self.rect)

        return action


class Oyuncu():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, oyunBittimi):
        dx = 0
        dy = 0
        yurumeHizi = 5
        genislik = 20

        if oyunBittimi == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.havada == False and self.havadami == False:
                ziplamaSes.play()
                self.y_hiz = -15
                self.havada = True
            if key[pygame.K_SPACE] == False:
                self.havada = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.sayac += 1
                self.yon = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.sayac += 1
                self.yon = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.sayac = 0
                self.index = 0
                if self.yon == 1:
                    self.image = self.sagResim[self.index]
                if self.yon == -1:
                    self.image = self.solResim[self.index]


            if self.sayac > yurumeHizi:
                self.sayac = 0    
                self.index += 1
                if self.index >= len(self.sagResim):
                    self.index = 0
                if self.yon == 1:
                    self.image = self.sagResim[self.index]
                if self.yon == -1:
                    self.image = self.solResim[self.index]

            self.y_hiz += 1
            if self.y_hiz > 10:
                self.y_hiz = 10
            dy += self.y_hiz

            self.havadami = True
            for kare in seviye.blokListesi:
                if kare[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if kare[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.y_hiz < 0:
                        dy = kare[1].bottom - self.rect.top
                        self.y_hiz = 0
                    elif self.y_hiz >= 0:
                        dy = kare[1].top - self.rect.bottom
                        self.y_hiz = 0
                        self.havadami = False


            if pygame.sprite.spritecollide(self, yaratiklar, False):
                oyunBittimi = -1
                oyunBittiSes.play()

            if pygame.sprite.spritecollide(self, lavlar, False):
                oyunBittimi = -1
                oyunBittiSes.play()

            if pygame.sprite.spritecollide(self, cikislar, False):
                oyunBittimi = 1

            for platform in platformlar:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if abs((self.rect.top + dy) - platform.rect.bottom) < genislik:
                        self.y_hiz = 0
                        dy = platform.rect.bottom - self.rect.top
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < genislik:
                        self.rect.bottom = platform.rect.top - 1
                        self.havadami = False
                        dy = 0
                    if platform.xHareket != 0:
                        self.rect.x += platform.hareketYonu

            self.rect.x += dx
            self.rect.y += dy

        elif oyunBittimi == -1:
            self.image = self.olumResmi
            metinYazdir('Oyun Bitti!', font, mavi, (ekran_gen // 2) - 100, ekran_yuk // 2)
            if self.rect.y > 200:
                self.rect.y -= 5

        ekran.blit(self.image, self.rect)

        return oyunBittimi


    def reset(self, x, y):
        self.sagResim = []
        self.solResim = []
        self.index = 0
        self.sayac = 0
        for indx in range(1, 5):
            sagResim = pygame.image.load(f'resim/steve{indx}.png')
            sagResim = pygame.transform.scale(sagResim, (40, 80))
            solResim = pygame.transform.flip(sagResim, True, False)
            self.sagResim.append(sagResim)
            self.solResim.append(solResim)
        self.olumResmi = pygame.image.load('resim/hayalet.png')
        self.image = self.sagResim[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.y_hiz = 0
        self.havada = False
        self.yon = 0
        self.havadami = True



class World():
    def __init__(self, dunyaVeri):
        self.blokListesi = []

        toprakResim = pygame.image.load('resim/toprak.png')
        cimenResim = pygame.image.load('resim/cimen.png')

        satirSayisi = 0
        for satir in dunyaVeri:
            sutunSayisi = 0
            for kare in satir:
                if kare == 1:
                    resim = pygame.transform.scale(toprakResim, (kareBoyutu, kareBoyutu))
                    resimKare = resim.get_rect()
                    resimKare.x = sutunSayisi * kareBoyutu
                    resimKare.y = satirSayisi * kareBoyutu
                    kare = (resim, resimKare)
                    self.blokListesi.append(kare)
                if kare == 2:
                    resim = pygame.transform.scale(cimenResim, (kareBoyutu, kareBoyutu))
                    resimKare = resim.get_rect()
                    resimKare.x = sutunSayisi * kareBoyutu
                    resimKare.y = satirSayisi * kareBoyutu
                    kare = (resim, resimKare)
                    self.blokListesi.append(kare)
                if kare == 3:
                    yaratik = Dusman(sutunSayisi * kareBoyutu, satirSayisi * kareBoyutu + 15)
                    yaratiklar.add(yaratik)
                if kare == 4:
                    platform = Platform(sutunSayisi * kareBoyutu, satirSayisi * kareBoyutu, 1, 0)
                    platformlar.add(platform)
                if kare == 5:
                    platform = Platform(sutunSayisi * kareBoyutu, satirSayisi * kareBoyutu, 0, 1)
                    platformlar.add(platform)
                if kare == 6:
                    lav = Lav(sutunSayisi * kareBoyutu, satirSayisi * kareBoyutu + (kareBoyutu // 2))
                    lavlar.add(lav)
                if kare == 7:
                    elmas = Altin(sutunSayisi * kareBoyutu + (kareBoyutu // 2), satirSayisi * kareBoyutu + (kareBoyutu // 2))
                    altinlar.add(elmas)
                if kare == 8:
                    cikis = Cikis(sutunSayisi * kareBoyutu, satirSayisi * kareBoyutu - (kareBoyutu // 2))
                    cikislar.add(cikis)
                sutunSayisi += 1
            satirSayisi += 1


    def draw(self):
        for kare in self.blokListesi:
            ekran.blit(kare[0], kare[1])


class Lav(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        resim = pygame.image.load('resim/lav.png')
        self.image = pygame.transform.scale(resim, (kareBoyutu, kareBoyutu // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Dusman(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('resim/yaratik.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hareketYonu = 1
        self.hareketSayaci = 0

    def update(self):
        self.rect.x += self.hareketYonu
        self.hareketSayaci += 1
        if abs(self.hareketSayaci) > 50:
            self.hareketYonu *= -1
            self.hareketSayaci *= -1


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, xHareket, yHareket):
        pygame.sprite.Sprite.__init__(self)
        resim = pygame.image.load('resim/platform.png')
        self.image = pygame.transform.scale(resim, (kareBoyutu, kareBoyutu // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hareketSayaci = 0
        self.hareketYonu = 1
        self.xHareket = xHareket
        self.yHareket = yHareket


    def update(self):
        self.rect.x += self.hareketYonu * self.xHareket
        self.rect.y += self.hareketYonu * self.yHareket
        self.hareketSayaci += 1
        if abs(self.hareketSayaci) > 50:
            self.hareketYonu *= -1
            self.hareketSayaci *= -1


class Altin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        resim = pygame.image.load('resim/elmas.png')
        self.image = pygame.transform.scale(resim, (kareBoyutu // 2, kareBoyutu // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Cikis(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        resim = pygame.image.load('resim/cikis.png')
        self.image = pygame.transform.scale(resim, (kareBoyutu, int(kareBoyutu * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y



oyuncu = Oyuncu(100, ekran_yuk - 130)

yaratiklar = pygame.sprite.Group()
platformlar = pygame.sprite.Group()
lavlar = pygame.sprite.Group()
altinlar = pygame.sprite.Group()
cikislar = pygame.sprite.Group()

altinSkoru = Altin(kareBoyutu // 2, kareBoyutu // 2)
altinlar.add(altinSkoru)

if path.exists(f'seviye{seviyeIndex}_data'):
    pickle_yukleyici = open(f'seviye{seviyeIndex}_data', 'rb')
    seviyeBilgisi = pickle.load(pickle_yukleyici)
seviye = World(seviyeBilgisi)


restartButton = Button(ekran_gen // 2 - 50, ekran_yuk // 2 + 100, tekrarAsset)
startButton = Button(ekran_gen // 2 - 350, ekran_yuk // 2, baslatAsset)
cikisButton = Button(ekran_gen // 2 + 150, ekran_yuk // 2, cikisAsset)


run = True
while run:

    sayac.tick(fps)

    ekran.blit(bgAsset, (0, 0))
    ekran.blit(gunesAsset, (100, 100))

    if anaMenu == True:
        if cikisButton.draw():
            run = False
        if startButton.draw():
            anaMenu = False
    else:
        seviye.draw()

        if oyunBittimi == 0:
            yaratiklar.update()
            platformlar.update()
            if pygame.sprite.spritecollide(oyuncu, altinlar, True):
                score += 1
                altinSes.play()
            metinYazdir('X ' + str(score), skor_font, beyaz, kareBoyutu - 10, 10)
        
        yaratiklar.draw(ekran)
        platformlar.draw(ekran)
        lavlar.draw(ekran)
        altinlar.draw(ekran)
        cikislar.draw(ekran)

        oyunBittimi = oyuncu.update(oyunBittimi)

        if oyunBittimi == -1:
            if restartButton.draw():
                seviyeBilgisi = []
                seviye = seviyeyiSifirla(seviyeIndex)
                oyunBittimi = 0
                score = 0

        if oyunBittimi == 1:
            seviyeIndex += 1
            if seviyeIndex <= tumSeviyeler:
                seviyeBilgisi = []
                seviye = seviyeyiSifirla(seviyeIndex)
                oyunBittimi = 0
            else:
                metinYazdir('Tebrikler Kazandınız!', font, mavi, (ekran_gen // 2) - 140, ekran_yuk // 2)
                if restartButton.draw():
                    seviyeIndex = 1
                    seviyeBilgisi = []
                    seviye = seviyeyiSifirla(seviyeIndex)
                    oyunBittimi = 0
                    score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
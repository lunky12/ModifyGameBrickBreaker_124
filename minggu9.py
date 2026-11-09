import pygame
import random
from pathlib import Path

pygame.init()
pygame.mixer.init()

# Dimensions of the screen
WIDTH, HEIGHT = 600, 500

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

font = pygame.font.Font('freesansbold.ttf', 15)
largeFont = pygame.font.Font('freesansbold.ttf', 30)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Breaker - Modified with SFX")

# to control the frame rate
clock = pygame.time.Clock()
FPS = 60

BG_IMAGE_NAME = "54a7d47d94eb1a8962caf1f36ea91f2e.jpg"
backgroundImage = pygame.image.load(
    Path(__file__).resolve().parent / BG_IMAGE_NAME
).convert()
imageWidth, imageHeight = backgroundImage.get_size()
scale = max(WIDTH / imageWidth, HEIGHT / imageHeight)
scaledSize = (int(imageWidth * scale), int(imageHeight * scale))
backgroundImage = pygame.transform.smoothscale(backgroundImage, scaledSize)
cropX = (scaledSize[0] - WIDTH) // 2
cropY = (scaledSize[1] - HEIGHT) // 2
backgroundImage = backgroundImage.subsurface(
    (cropX, cropY, WIDTH, HEIGHT)
).copy()
backgroundOverlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
backgroundOverlay.fill((0, 0, 0, 100))


def drawBackground():
    screen.blit(backgroundImage, (0, 0))
    screen.blit(backgroundOverlay, (0, 0))


# Striker class
class Striker:
    def __init__(self, posx, posy, width, height, speed, color):
        self.posx, self.posy = posx, posy
        self.width, self.height = width, height
        self.speed = speed
        self.color = color

        self.strikerRect = pygame.Rect(self.posx, self.posy, self.width, self.height)

    def display(self):
        pygame.draw.rect(screen, self.color, self.strikerRect)

    def update(self, xFac):
        self.posx += self.speed * xFac

        # Restricting the striker to be in between the edges
        if self.posx <= 0:
            self.posx = 0
        elif self.posx + self.width >= WIDTH:
            self.posx = WIDTH - self.width

        self.strikerRect = pygame.Rect(self.posx, self.posy, self.width, self.height)

    def getRect(self):
        return self.strikerRect


# Block Class
class Block:
    def __init__(self, posx, posy, width, height, color):
        self.posx, self.posy = posx, posy
        self.width, self.height = width, height
        self.color = color
        self.damage = 100

        # White blocks have health 200 (need 2 hits), Green have 100 (1 hit)
        if color == WHITE:
            self.health = 200
        else:
            self.health = 100

        self.blockRect = pygame.Rect(self.posx, self.posy, self.width, self.height)

    def display(self):
        if self.health > 0:
            pygame.draw.rect(screen, self.color, self.blockRect)

    def hit(self):
        self.health -= self.damage

    def getRect(self):
        return self.blockRect

    def getHealth(self):
        return self.health


# Ball Class
class Ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.posx, self.posy = posx, posy
        self.radius = radius
        self.speed = speed
        self.color = color
        self.xFac, self.yFac = 1, 1

    def display(self):
        pygame.draw.circle(screen, self.color, (int(self.posx), int(self.posy)), self.radius)

    def update(self):
        self.posx += self.xFac * self.speed
        self.posy += self.yFac * self.speed

        # Reflecting from vertical edges
        if self.posx <= 0 or self.posx >= WIDTH:
            self.xFac *= -1

        # Reflection from top edge
        if self.posy <= 0:
            self.yFac *= -1

        # If ball touches bottom edge, return True (life lost)
        if self.posy >= HEIGHT:
            return True

        return False

    def reset(self):
        self.posx = WIDTH // 2
        self.posy = HEIGHT // 2
        self.xFac, self.yFac = 1, -1

    def hit(self):
        self.yFac *= -1

    def getRect(self):
        # Return a rect approximation for the circle collision
        return pygame.Rect(self.posx - self.radius, self.posy - self.radius, self.radius * 2, self.radius * 2)


# Helper Functions
def collisionChecker(rect, ballRect):
    return pygame.Rect.colliderect(rect, ballRect)


def populateBlocks(blockWidth, blockHeight, horizontalGap, verticalGap):
    listOfBlocks = []
    for i in range(10, WIDTH - blockWidth, blockWidth + horizontalGap):
        for j in range(40, HEIGHT // 2, blockHeight + verticalGap):
            listOfBlocks.append(
                Block(i, j, blockWidth, blockHeight, random.choice([WHITE, GREEN]))
            )
    return listOfBlocks


# Fungsi Game Over dengan tampilan teks & SFX Game Over
def gameOver(score, gameOverSound):
    gameOverSound.play()  # Memutar SFX saat game over
    while True:
        drawBackground()
        
        # Render Game Over Text
        goText = largeFont.render("GAME OVER", True, RED)
        goRect = goText.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        
        scoreText = font.render(f"Final Score: {score}", True, WHITE)
        scoreRect = scoreText.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        restartText = font.render("Press SPACE to Restart or ESC to Exit", True, YELLOW)
        restartRect = restartText.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        
        screen.blit(goText, goRect)
        screen.blit(scoreText, scoreRect)
        screen.blit(restartText, restartRect)
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False


# Game Manager
def main():
    running = True
    lives = 3
    score = 0

    soundDir = Path(__file__).resolve().parent
    bounceSound = pygame.mixer.Sound(soundDir / "bounce.wav")
    hitSound = pygame.mixer.Sound(soundDir / "hit.wav")
    breakSound = pygame.mixer.Sound(soundDir / "break.wav")
    lifeLostSound = pygame.mixer.Sound(soundDir / "life_lost.wav")
    gameOverSound = pygame.mixer.Sound(soundDir / "gameover.wav")
    for sound in (bounceSound, hitSound, breakSound, lifeLostSound, gameOverSound):
        sound.set_volume(0.45)

    striker = Striker(WIDTH // 2 - 50, HEIGHT - 40, 100, 15, 8, WHITE)
    strikerXFac = 0

    ball = Ball(WIDTH // 2, HEIGHT // 2, 8, 4, WHITE)

    blockWidth, blockHeight = 50, 15
    horizontalGap, verticalGap = 15, 15

    listOfBlocks = populateBlocks(blockWidth, blockHeight, horizontalGap, verticalGap)

    # Game loop
    while running:
        drawBackground()

        # Render UI Score & Lives
        scoreSurface = font.render(f"Score : {score}", True, WHITE)
        livesSurface = font.render(f"Lives : {lives}", True, WHITE)
        screen.blit(scoreSurface, (20, HEIGHT - 25))
        screen.blit(livesSurface, (WIDTH - 100, HEIGHT - 25))

        # Repopulate blocks if all destroyed
        if not listOfBlocks:
            listOfBlocks = populateBlocks(blockWidth, blockHeight, horizontalGap, verticalGap)
            ball.speed += 1  # Bonus kecepatan naik sedikit tiap ganti level/stage baru!

        # Game Over Condition
        if lives <= 0:
            shouldRestart = gameOver(score, gameOverSound)
            if shouldRestart:
                lives = 3
                score = 0
                ball.speed = 4
                listOfBlocks = populateBlocks(blockWidth, blockHeight, horizontalGap, verticalGap)
                ball.reset()
            else:
                running = False

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    strikerXFac = -1
                if event.key == pygame.K_RIGHT:
                    strikerXFac = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    strikerXFac = 0

        # Collision check: Striker & Ball
        if collisionChecker(striker.getRect(), ball.getRect()):
            ball.hit()
            bounceSound.play()  # SFX saat bola memantul dari striker

        # Collision check: Blocks & Ball
        for block in listOfBlocks[:]:
            if collisionChecker(block.getRect(), ball.getRect()):
                ball.hit()
                block.hit()

                if block.getHealth() <= 0:
                    breakSound.play()
                    listOfBlocks.remove(block)
                    if block.color == WHITE:
                        score += 10
                    else:
                        score += 5
                    
                    if score % 50 == 0:
                        ball.speed += 0.5
                else:
                    hitSound.play()

                break  # Break to prevent multi-collision glitch in one frame

        # Update positions
        striker.update(strikerXFac)
        lifeLost = ball.update()

        if lifeLost:
            lives -= 1
            lifeLostSound.play()
            ball.reset()

        # Display objects
        striker.display()
        ball.display()

        for block in listOfBlocks:
            block.display()

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
    pygame.quit()
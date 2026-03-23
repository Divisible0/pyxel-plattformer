
import pyxel

#World size
WORLD_WIDTH = 1080
WORLD_HEIGHT = 720



#Camera Size
VIEW_WIDTH = 360
VIEW_HEIGHT = 240


def clamp(value, minimum, maximum): # Prevents camera from clipping
    return max(minimum, min(value, maximum))

def collision(ax, ay, aw, ah, bx, by, bw, bh): 
    return (
        ax < bx + bw and ax + aw > bx and
        ay < by + bh and ay + ah > by
    )

class BackgroundLayer:
    def __init__(self, filename, parallax_x=1.0, parallax_y=1.0):
        self.image = pyxel.Image(WORLD_WIDTH, WORLD_HEIGHT)
        self.image.load(0, 0, filename)
        self.parallax_x = parallax_x
        self.parallax_y = parallax_y

    def draw(self, colkey=0):
        src_u = int(camera_x * self.parallax_x)
        src_v = int(camera_y * self.parallax_y)
        pyxel.blt(camera_x, camera_y, self.image, src_u, src_v, VIEW_WIDTH, VIEW_HEIGHT, colkey)

class Player:
    def __init__(self):
        self.x = 120
        self.y = 704

        self.w = 16
        self.h = 16

        # Hitbox width/height & position (centered)
        self.hitbox_w = 12
        self.hitbox_h = 15
        self.hitbox_offset_x = 2 
        self.hitbox_offset_y = 1

        self.vx = 0
        self.vy = 0
        self.gravity = 0.8
        self.accel_ground = 0.7
        self.accel_air = 0.3
        self.friction_air = 0.9
        self.friction_ground = 0.01
        self.max_fall = 8
        self.max_speed = 4
        self.on_ground = False
        self.air = False
        self.state = "idle"
        self.stamina = 0
        self.dash_timer = 0

    def hitbox(self):
        return (
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            self.hitbox_w,
            self.hitbox_h
    )

    def update(self):
        self.stamina += 1
        if self.dash_timer > 0:
            self.dash_timer -= 1
        else:
            if self.vx > self.max_speed:
                self.vx = self.max_speed
            if self.vx < -self.max_speed:
                self.vx = -self.max_speed
        
        if self.on_ground:
            accel = self.accel_ground
            friction = self.friction_ground
            self.air = False
        else:
            accel = self.accel_air
            friction = self.friction_air
            self.air = True

        if self.on_ground and pyxel.btnp(pyxel.KEY_SPACE):
            self.vy = -9
        if pyxel.btn(pyxel.KEY_D):
            if self.on_ground and self.vx < 0:
                self.vx = 0
            self.vx += accel
            self.state = "facing_right"
        elif pyxel.btn(pyxel.KEY_A):
            if self.on_ground and self.vx > 0:
                self.vx = 0
            self.vx -= accel
            self.state ="facing_left"
        elif self.dash_timer <= 0:
            self.vx *= (friction)
            if abs(self.vx) < 0.05:
                self.vx = 0
        if pyxel.btn(pyxel.KEY_LSHIFT) and self.stamina >= 30:
            self.stamina = 0
            self.dash_timer = 6
            if self.state == "facing_right":
                self.vx = 9
            elif self.state == "facing_left":
                self.vx = -9
            

        # Movement Model
        global u, v
        u, v = 0, 0
        if self.state == "idle" and self.air == False:
            u, v = 0, 0
        elif self.state == "facing_right" and self.air == False:
            u, v = 0, 32
        elif self.state == "facing_left" and self.air == False:
            u, v = 0, 16
        elif self.state == "idle" and self.air == True:
            u, v = 0, 80
        elif self.state == "facing_right" and self.air == True:
            u, v, = 0, 48
        elif self.state == "facing_left" and self.air == True:
            u, v = 0, 64
        else:
            u, v = 0, 0


        self.vy += self.gravity
        if self.vy > self.max_fall:
            self.vy = self.max_fall

        old_x = self.x
        old_y = self.y
        old_hx = old_x + self.hitbox_offset_x
        old_hy = old_y + self.hitbox_offset_y

        self.x += self.vx
        self.y += self.vy

        self.on_ground = False

        # World floor (fallback)
        if self.y > WORLD_HEIGHT - self.h:
            self.y = WORLD_HEIGHT - self.h
            self.vy = 0
            self.on_ground = True

        hx, hy, hw, hh = self.hitbox()

        # Platform collisions
        for p in platforms:
            if collision(hx, hy, hw, hh, p.x, p.y, p.w, p.h):

                # Coming from above (landing)
                if old_hy + hh <= p.y and hy + hh > p.y:
                    self.y = p.y - self.hitbox_h - self.hitbox_offset_y
                    self.vy = 0
                    self.on_ground = True

                # Coming from below (head bump)
                elif old_hy >= p.y + p.h and hy < p.y + p.h:
                    self.y = p.y + p.h - self.hitbox_offset_y
                    self.vy = 0

                # Coming from left
                elif old_hx + hw <= p.x and hx + hw > p.x:
                    self.x = p.x - self.hitbox_w - self.hitbox_offset_x
                    self.vx = 0

                # Coming from right
                elif old_hx >= p.x + p.w and hx < p.x + p.w:
                    self.x = p.x + p.w - self.hitbox_offset_x
                    self.vx = 0

    def draw(self):
        pyxel.blt(self.x, self.y, 0, u, v, 16, 16, 0)


class Platform:
    def __init__(self, x, y, w, h): #Platform properties can be defined later
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw(self):
        tiles = max(1, self.w // 16) #Calculates the width of the plattform into whole blocks (pixel/16)
        for i in range(tiles):
            pyxel.blt(self.x + i * 16, self.y, 0, 16, 0, 16, 16, 0)

camera_x = 0
camera_y = 0

def update_camera(): #Function to update camera
    global camera_x, camera_y # Sets camera_x and camera_y to be global (available not only in the function)

    target_x = player.x + player.w / 2 - VIEW_WIDTH / 2 #Calculates Camera Position (x)
    target_y = player.y + player.h / 2 - VIEW_HEIGHT / 2 #Calculates Camera Position (y)

    camera_x = clamp(target_x, 0, WORLD_WIDTH - VIEW_WIDTH) # Prevents camera from clipping out of the world (x)
    camera_y = clamp(target_y, 0, WORLD_HEIGHT - VIEW_HEIGHT) # Prevents camera from clipping out of the world (y)

player = Player()
platforms = [
    Platform(512, 688, 64, 16),
    Platform(368, 656, 64, 16),
    Platform(496, 624, 64, 16),
    Platform(656, 608, 64, 16),
    Platform(800, 578, 64, 16)
    ]

backgrounds = [
    BackgroundLayer("assets/Back2.png", parallax_x=0.6, parallax_y=1.0),
    BackgroundLayer("assets/Back.png",  parallax_x=0.7, parallax_y=1.0),
    BackgroundLayer("assets/Mid.png",   parallax_x=0.9, parallax_y=1.0),
    BackgroundLayer("assets/Front.png", parallax_x=1.0, parallax_y=1.0),
]

def update():
    player.update()
    update_camera()

def draw():
    pyxel.cls(0) #Clears Screen
    pyxel.camera(camera_x, camera_y) #Camera Position (set in update_camera)
    backgrounds[0].draw()  # Back2 - kein colkey, alles sichtbar
    for bg in backgrounds[1:]:  # Back, Mid, Front - transparent
        bg.draw(colkey=7)
    player.draw() #Draws player
    for p in platforms: #Draws all the plattforms
        p.draw()

pyxel.init(VIEW_WIDTH, VIEW_HEIGHT, display_scale=3) #Smaller view = zoomed camera
pyxel.colors[1] = 0x000000 #Reassign colors (black)
pyxel.load("assets/resources.pyxres")
pyxel.run(update, draw) #Executes the draw function & updates (every frame)

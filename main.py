
import pyxel

#World size
WORLD_WIDTH = 1080
WORLD_HEIGHT = 720

#Camera Size
VIEW_WIDTH = 360
VIEW_HEIGHT = 240


def clamp(value, minimum, maximum): #Used to prevent any value going over their maximum. Later used to prevent camera from exiting the world
    return max(minimum, min(value, maximum))

# AABB collision check
def aabb(ax, ay, aw, ah, bx, by, bw, bh): 
    return (
        ax < bx + bw and ax + aw > bx and
        ay < by + bh and ay + ah > by
    )

class Player:
    def __init__(self):
        self.x = 120 #Starting Position
        self.y = 704

        self.w = 16 #Width
        self.h = 16 #Height

        # Hitbox width/height
        self.hitbox_w = 12
        self.hitbox_h = 15

        #Empty space
        self.hitbox_offset_x = 2 
        self.hitbox_offset_y = 1

        self.vx = 0 #Starting Velocity
        self.vy = 0
        self.gravity = 0.8 #Gravity
        self.accel_ground = 0.7 #Acceleration on the floor
        self.accel_air = 0.2 #Acceleration in the air
        self.friction_air = 0.9
        self.friction_ground = 0.01
        self.max_fall = 8 #Prevents clipping
        self.max_speed = 4 #Sets Max Speed
        self.on_ground = False #Statement gets changed when on a plattform

        self.hp = 20 #Hp

    def hitbox(self):
        return (
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            self.hitbox_w,
            self.hitbox_h
    )

    def update(self):
        if self.vx > self.max_speed: #speed limit (positive x)
            self.vx = self.max_speed 
        if self.vx < -self.max_speed: #speed limit (negative x)
            self.vx = -self.max_speed 
        
        # When in the air/on the ground uses the apropriate acceleration property
        if self.on_ground:
            accel = self.accel_ground
        else:
            accel = self.accel_air

        #Sets movement
        if self.on_ground and pyxel.btnp(pyxel.KEY_SPACE):
            self.vy = -9
        if pyxel.btn(pyxel.KEY_D):
            self.vx += accel #Uses the acceleration property to move
        elif pyxel.btn(pyxel.KEY_A):
            self.vx -= accel #Uses the acceleration property to move
        else:
            #  No input -> slow down
            self.vx *= (self.friction_ground if self.on_ground else self.friction_air)
            if abs(self.vx) < 0.05:
                self.vx = 0

        # Saves current Position in case of colision
        old_x = self.x
        old_y = self.y

        self.vy += self.gravity
        if self.vy > self.max_fall:  # Limits fall speed (clipping)
            self.vy = self.max_fall

        #Apply Movement
        self.x += self.vx
        self.y += self.vy

        # Will be set to True again when landing on something
        self.on_ground = False

        # World floor (fallback)
        if self.y > WORLD_HEIGHT - self.h:
            self.y = WORLD_HEIGHT - self.h
            self.vy = 0
            self.on_ground = True

        hx, hy, hw, hh = self.hitbox() #Assigns the hitbox values for the collision calculation

        #saves position before collision (including hitbox properties)
        old_hx = old_x + self.hitbox_offset_x 
        old_hy = old_y + self.hitbox_offset_y

        # Platform collisions
        for p in platforms:
            if aabb(hx, hy, hw, hh, p.x, p.y, p.w, p.h):

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
        pyxel.blt(self.x, self.y, 0, 0, 0, 16, 16, 0)


class Platform:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw(self):
        tiles = max(1, self.w // 16) #Calculates the width of the plattform into whole blocks (pixel/16)
        for i in range(tiles): #repeats the process that many times
            pyxel.blt(self.x + i * 16, self.y, 0, 16, 0, 16, 16, 0) #builds the squares next to eachother


#sets the upper left edge of the camera (width is set in the top of the code)
#this point is later moved to match the player position
camera_x = 0
camera_y = 0

def update_camera(): #Function to update camera
    global camera_x, camera_y # Sets camera_x and camera_y to be global (available not only in the function)

    target_x = player.x + player.w / 2 - VIEW_WIDTH / 2 #Calculates Camera Position (x)
    target_y = player.y + player.h / 2 - VIEW_HEIGHT / 2 #Calculates Camera Position (y)

    camera_x = clamp(target_x, 0, WORLD_WIDTH - VIEW_WIDTH) # Prevents camera from clipping out of the world (x)
    camera_y = clamp(target_y, 0, WORLD_HEIGHT - VIEW_HEIGHT) # Prevents camera from clipping out of the world (y)

#Assign variables/lists to the classes (to draw them)
player = Player()
platforms = [
    Platform(512, 688, 64, 16),
    Platform(368, 656, 64, 16),
    Platform(496, 624, 64, 16),
    Platform(656, 608, 64, 16),
    Platform(800, 578, 64, 16)
    ]

#The draw function repeats itself every frame
def draw():
    update_camera() #Camera Position
    pyxel.cls(2) #Clears Screen
    pyxel.colors[15] = 0x525252
    pyxel.colors[1] = 0x000000
    pyxel.bltm(0, 0, 0, 0, -112, 360, 240, 0)
    pyxel.camera(camera_x, camera_y) #Camera Position (set in update_camera)
    player.draw() #Draws player
    for p in platforms: #Draws all the plattforms
        p.draw()

    pyxel.camera(0, 0)

pyxel.init(VIEW_WIDTH, VIEW_HEIGHT, display_scale=3) #Smaller view = zoomed camera


pyxel.load("assets/resources.pyxres")
pyxel.run(player.update, draw) #Executes the draw function & updates (every frame)

import pyxel

# AABB collision check
def aabb(ax, ay, aw, ah, bx, by, bw, bh): 
    return (
        ax < bx + bw and ax + aw > bx and
        ay < by + bh and ay + ah > by
    )

class Player:
    def __init__(self):
        self.x = 704 #Starting Position
        self.y = 704

        self.w = 16 #Width
        self.h = 16 #Height

        self.vx = 0 #Starting Velocity
        self.vy = 0
        self.gravity = 0.6 #Gravity
        self.accel_ground = 0.6 #Acceleration on the floor
        self.accel_air = 0.2 #Acceleration in the air
        self.friction_air = 0.9
        self.friction_ground = 0.1
        self.max_fall = 8 #Prevents clipping
        self.max_speed = 4 #Sets Max Speed
        self.on_ground = False #Statement gets changed when on a plattform

        self.hp = 20 #Hp
        pyxel.image(0).load(0, 0, "assets/player.png") #Sprite

    def update(self):
        if self.vx > self.max_speed: self.vx = self.max_speed
        if self.vx < -self.max_speed: self.vx = -self.max_speed
        
        if self.on_ground:
            accel = self.accel_ground
        else:
            accel = self.accel_air

        if self.on_ground and pyxel.btnp(pyxel.KEY_SPACE):
            self.vy = -8
        if pyxel.btn(pyxel.KEY_D):
            self.vx += accel
        elif pyxel.btn(pyxel.KEY_A):
            self.vx -= accel
        else:
            #  No input -> slow down
            self.vx *= (self.friction_ground if self.on_ground else self.friction_air)
            if abs(self.vx) < 0.05:
                self.vx = 0

        # Saves Position in case of colision
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
        if self.y > 704:
            self.y = 704
            self.vy = 0
            self.on_ground = True

        # Platform collisions
        for p in platforms:
            if aabb(self.x, self.y, self.w, self.h, p.x, p.y, p.w, p.h):
                # Coming from above (landing)
                if old_y + self.h <= p.y and self.y + self.h > p.y:
                    self.y = p.y - self.h
                    self.vy = 0
                    self.on_ground = True

                # Coming from below (head bump)
                elif old_y >= p.y + p.h and self.y < p.y + p.h:
                    self.y = p.y + p.h
                    self.vy = 0

                # Coming from left
                elif old_x + self.w <= p.x and self.x + self.w > p.x:
                    self.x = p.x - self.w
                    self.vx = 0

                # Coming from right
                elif old_x >= p.x + p.w and self.x < p.x + p.w:
                    self.x = p.x + p.w
                    self.vx = 0

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 0, 0, 16, 16)



class Platform:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        pyxel.image(1).load(0, 0, "assets/block.png")
    
    def draw(self):
        tiles = max(1, self.w // 16) #Calculates the width of the plattform into whole blocks (pixel/16)
        for i in range(tiles): #repeats the process that many times
            pyxel.blt(self.x + i * 16, self.y, 1, 0, 0, 16, 16) #builds the squares next to eachother


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
    pyxel.cls(0) #Clears Screen
    player.draw() #Draws player
    for p in platforms: #Draws all the plattforms
        p.draw()
    
pyxel.init(1080,720) #Game window size
pyxel.run(player.update, draw) #Executes the draw function & updates (every frame)
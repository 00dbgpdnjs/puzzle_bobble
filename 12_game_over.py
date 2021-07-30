import os, random, math
import pygame

class Bubble(pygame.sprite.Sprite):
    def __init__(self, image, color, position=(0,0), row_idx=-1, col_idx=-1): # =(0,0) : init; I can make Bubble object without position like this 'Bubble(image, color)'/ -1 ?? 2:52:00
        super().__init__()
        self.image = image
        self.color = color
        self.rect = image.get_rect(center=position)
        self.radius = 13 # = R : Firing Speed Control; Refer to bubble_move.png
        self.row_idx = row_idx
        self.col_idx = col_idx

    def set_rect(self, position):
        self.rect = self.image.get_rect(center=position)

    def draw(self, screen, to_x=None): # ?? -> Check create_bubble() / None: when more than 3 chances left
        if to_x:
            screen.blit(self.image, (self.rect.x + to_x, self.rect.y))
        else:
            screen.blit(self.image, self.rect) # (what, where)

    def set_angle(self, angle):
        self.angle = angle
        self.rad_angle = math.radians(self.angle)

    def move(self): # Refer to bubble_move.png
        to_x = self.radius * math.cos(self.rad_angle)
        to_y = self.radius * math.sin(self.rad_angle) * -1 # * 1 : down

        self.rect.x += to_x
        self.rect.y += to_y
        
        # Reverse 'A angle' to '180-A angle'.
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.set_angle(180 - self.angle)

    # After curr_bubble collide, got the location.
    def set_map_index(self, row_idx, col_idx):
        self.row_idx = row_idx
        self.col_idx = col_idx

    def drop_downward(self, height):
        self.rect = self.image.get_rect(center=(self.rect.centerx, self.rect.centery + height))

class Pointer(pygame.sprite.Sprite):
    def __init__(self, image, position, angle):
        super().__init__()
        self.image = image # whenever the angle changes, this var is updated
        self.rect = image.get_rect(center=position)
        self.angle = angle
        self.original_image = image # Rotating a image to fit the angle: not continuously adding to the rotated image, but with the original image (0 degrees).
        self.position = position

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # pygame.draw.circle(screen, RED, self.position, 3)

    def rotate(self, angle): # 2nd arg get to_angle. And add this angle to Pointer's angle like the code below
        self.angle += angle        

        if self.angle > 170:
            self.angle = 170
        elif self.angle < 10:
            self.angle = 10

        # (image to rotate, how much, no size transformation)
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        self.rect = self.image.get_rect(center=self.position)

# Making a Map
def setup():
    global map
    # map = [ # map.png
    #     list("RRYYBBGG"), # = ["R", "R", "Y", "Y", "B", "B", "G", "G"]
    #     list("RRYYBBG/"), # / : Where bubbles cannot be located
    #     list("BBGGRRYY"),
    #     list("BGGRRYY/"),
    #     list("........"), # an empty place
    #     list("......./"),
    #     list("........"),
    #     list("......./"),
    #     list("........"),
    #     list("......./"),
    #     list("........")
    # ]

    # # lv2
    # map = [
    #     list("...YY..."),
    #     list("...G.../"),
    #     list("...R...."),
    #     list("...B.../"),
    #     list("...R...."),
    #     list("...G.../"),
    #     list("...P...."),
    #     list("...P.../"),
    #     list("........"),
    #     list("......./"),
    #     list("........")
    # ]    

    # high level
    map = [
        list("G......G"),
        list("RGBYRGB/"),
        list("Y......Y"),
        list("BYRGBYR/"),
        list("...R...."),
        list("...G.../"),
        list("...R...."),
        list("......./"),
        list("........"),
        list("......./"),
        list("........")
    ]

    for row_idx, row in enumerate(map): # Line by line
        for col_idx, col in enumerate(row):
            if col in [".", "/"]: # no bubble
                continue
            position = get_bubble_position(row_idx, col_idx)
            image = get_bubble_image(col)
            bubble_group.add(Bubble(image, col, position, row_idx, col_idx)) # all bubble are in bubble_group

def get_bubble_position(row_idx, col_idx): # map_pos.png
    pos_x = col_idx * CELL_SIZE + (BUBBLE_WIDTH // 2)
    pos_y = row_idx * CELL_SIZE + (BUBBLE_HEIGHT // 2) + wall_height
    if row_idx % 2 == 1: # Odd Number
        pos_x += CELL_SIZE // 2
    return pos_x, pos_y
    # return: position which call this func  will be got in the form of a tuple

def get_bubble_image(color):
    if color == "R":
        return bubble_images[0]
    elif color == "Y":
        return bubble_images[1]
    elif color == "B":
        return bubble_images[2]
    elif color == "G":
        return bubble_images[3]
    elif color == "P":
        return bubble_images[4]
    else: # BLACK
        return bubble_images[-1] # -1 : last idx

def prepare_bubbles():
    global curr_bubble, next_bubble
    if next_bubble:
        curr_bubble = next_bubble
    else: # no next_bubble when game start
        curr_bubble = create_bubble()

    curr_bubble.set_rect((screen_width // 2, 624))
    next_bubble = create_bubble()
    next_bubble.set_rect((screen_width // 4, 688))

def create_bubble():
    color = get_randome_bubble_color() # This code should be written before the code below. cuz of image by color
    image = get_bubble_image(color)
    return Bubble(image, color)

def get_randome_bubble_color(): # Only of the colors on the screen.
    colors = [] # candidate
    for row in map:
        for col in row:
            if col not in colors and col not in [".", "/"]:
                colors.append(col)
    return random.choice(colors) # Choice one of 'colors' and return this func

def process_collision():
    global curr_bubble, fire, curr_fire_count
    hit_bubble = pygame.sprite.spritecollideany(curr_bubble, bubble_group, pygame.sprite.collide_mask) # this method: bring collited curr_bubble to the var/ 3rd arg: How to process the collision/ collide_mask: exclude the transparent part; real image part/ any: If there's any collision even one
    if hit_bubble or curr_bubble.rect.top <= wall_height: # Collision on the ceiling = Reached at celling/ Refer to puzzle_bobble.txt
        row_idx, col_idx = get_map_index(*curr_bubble.rect.center) # idx of cur_bubble by its coordinates (= rect.center) / ~center is tuple. * : unpacking
        place_bubble(curr_bubble, row_idx, col_idx) #(what, where, where)
        remove_adjacent_bubbles(row_idx, col_idx, curr_bubble.color) # two args: from here, 3rd : can visit to same color bubbles
        curr_bubble = None # # Then new bubble is maden by prepare_bubbles()
        fire = False # # Then re-launchable status
        curr_fire_count -= 1

def get_map_index(x, y): # which map idx to put the bubble in a cell[map] / not ((x, y)) cuz it's unpacked
    row_idx = (y - wall_height) // CELL_SIZE # -wall_height ?? 
    # NB: if the location of a bubble fired is weird, the reason is wall_height
    col_idx = x // CELL_SIZE
    if row_idx % 2 == 1:
        col_idx = (x - (CELL_SIZE // 2)) // CELL_SIZE
        # Refer to bubble_NB.png
        if col_idx < 0:
            col_idx = 0
        elif col_idx > MAP_COLUMN_COUNT - 2:
            col_idx = MAP_COLUMN_COUNT - 2
    return row_idx, col_idx

def place_bubble(bubble, row_idx, col_idx):
    map[row_idx][col_idx] = bubble.color # To update on a map
    position = get_bubble_position(row_idx, col_idx)
    bubble.set_rect(position) # Change the location of the bubble to fit the cell
    bubble.set_map_index(row_idx, col_idx) # bubbles after started. not inited bubles. If a bubble is added in bubble_group, can't it automatically set the map-based location?? Does it only set for the initial bubbles??
    bubble_group.add(bubble) # To process the collision with this bubble and the entire bubble when the next bubble is fired. Refer to the 2nd arg of the first code of process_collision()

def remove_adjacent_bubbles(row_idx, col_idx, color):
    visited.clear() # Remove last record
    visit(row_idx, col_idx, color) # 벽에 의한 y 좌표: 방문하는 것은 맵 좌표기준이라 상관x ??
    if len(visited) >= 3:
        remove_visited_bubbles()
        remove_hanging_bubbles()

def visit(row_idx, col_idx, color=None):
    # None: cuz when checking hanging bubbles, color doesn't matter
    if row_idx < 0 or row_idx >= MAP_ROW_COUNT or col_idx < 0 or col_idx >= MAP_COLUMN_COUNT:
        return # Get out of this func
    if color and map[row_idx][col_idx] != color: # ??
        return
        # "!= color" includes "." and "/" So the code below is needed
    if map[row_idx][col_idx] in [".", "/"]:
        return
    if (row_idx, col_idx) in visited:
        return # Don't visit
    visited.append((row_idx, col_idx))

    #  Based on the current bubble, combine the two codes below each other; total adjacent 6 coordinates. Refer to pop2.png
    rows = [0, -1, -1, 0, 1, 1] 
    cols = [-1, -1, 0, 1, 0, -1]
    if row_idx % 2 == 1:
        rows = [0, -1, -1, 0, 1, 1]
        cols = [-1, 0, 1, 1, 1, 0]

    # Call recursive func. Change the location to visit. If there isn't thing to visit, it's escaped from visit func. Refer to recursive.py/png
    for i in range(len(rows)):
        visit(row_idx + rows[i], col_idx + cols[i], color)

def remove_visited_bubbles():
    # visited is a gloval var??
    bubbles_to_remove = [b for b in bubble_group if (b.row_idx, b.col_idx) in visited] # Bring to the first b from bubble_group and compare with the 2nd b?? / Based on map coordinates, wall height correlation x ??
    for bubble in bubbles_to_remove:
        map[bubble.row_idx][bubble.col_idx] = "."
        bubble_group.remove(bubble)

def remove_not_visited_bubbles():
    bubbles_to_remove = [b for b in bubble_group if (b.row_idx, b.col_idx) not in visited]
    for bubble in bubbles_to_remove:
        map[bubble.row_idx][bubble.col_idx] = "."
        bubble_group.remove(bubble)

def remove_hanging_bubbles(): # Refer to far_bubble.png
    visited.clear()
    # [0] : Check only 0 of row_idx
    for col_idx in range(MAP_COLUMN_COUNT):
        if map[0][col_idx] != ".":
            visit(0, col_idx)
    remove_not_visited_bubbles()

def draw_bubbles():
    to_x = None
    if curr_fire_count == 2:
        to_x = random.randint(0, 2) -1 # -1 ~ 1 / = just (-1, 1) / Randomly -1 to 1
    elif curr_fire_count == 1:
        to_x = random.randint(0, 4) - 2 # -2 ~ 2

    for bubble in bubble_group:
        bubble.draw(screen, to_x) # when drawn, add to_x to rect

# total 7 chance
# last 2 chances: the screen shakes a little
# last chance: the scree shakes badly
# all chances are gone: wall down
def drop_wall():
    global wall_height, curr_fire_count
    wall_height += CELL_SIZE
    for bubble in bubble_group:
        bubble.drop_downward(CELL_SIZE)
    curr_fire_count = FIRE_COUNT

def get_lowest_bubble_bottom():
    bubble_bottoms = [bubble.rect.bottom for bubble in bubble_group] # "what do you want; bottom coordinate of all b" for "one by one" in "where"
    return max(bubble_bottoms) # among the list above

def change_bubble_image(image):
    for bubble in bubble_group:
        bubble.image = image

def display_game_over():
    txt_game_over = game_font.render(game_result, True, WHITE) # (,arias,)
    rect_game_over = txt_game_over.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(txt_game_over, rect_game_over)

pygame.init()
screen_width = 448
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Puzzle Bobble")
clock = pygame.time.Clock() #FPS

current_path = os.path.dirname(__file__)
background = pygame.image.load(os.path.join(current_path, "background.png"))
wall = pygame.image.load(os.path.join(current_path, "wall.png"))

bubble_images = [
    pygame.image.load(os.path.join(current_path, "red.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path, "yellow.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path, "blue.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path, "green.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path, "purple.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path, "black.png")).convert_alpha()
]
# .convert_alpha() : transparency -> When dealing with collisions between bubbles, it is possible to deal with collisions on parts that actually have images, not on a rect basis.

pointer_image = pygame.image.load(os.path.join(current_path, "pointer.png"))
pointer = Pointer(pointer_image, (screen_width // 2, 624), 90) # 90: Set initial angle vertically

CELL_SIZE = 56
BUBBLE_WIDTH = 56
BUBBLE_HEIGHT = 62
RED = (250, 0, 0)
WHITE = (255, 255, 255)
MAP_ROW_COUNT = 11
MAP_COLUMN_COUNT = 8
FIRE_COUNT = 7

#to_angle = 0 # the info of movement to left and right / this code is not good than two codes below
to_angle_left = 0
to_angle_right = 0
angle_speed = 1.5 # move at 1.5 degrees.

curr_bubble = None # a bubble to fire
next_bubble = None 
fire = False # fire status: Whether it's firing or not. If so, can't fire
curr_fire_count = FIRE_COUNT
wall_height = 0 # The height of the wall shown on the screen

is_game_over = False
game_font = pygame.font.SysFont("arialrounded", 40) # (,size)
game_result = None

map = []
visited = [] # Record Visited Locations
bubble_group = pygame.sprite.Group()
setup()

running = True
while running:
    clock.tick(60) # (FPS) speed 60

    for event in pygame.event.get():
        if event.type == pygame.QUIT: # Close the window; Click x btn
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                to_angle_left += angle_speed
            elif event.key == pygame.K_RIGHT:
                to_angle_right -= angle_speed
            elif event.key == pygame.K_SPACE:
                if curr_bubble and not fire:
                    fire = True
                    curr_bubble.set_angle(pointer.angle)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                to_angle_left = 0 # 0?? -> Check rotate()
            elif event.key == pygame.K_RIGHT:
                to_angle_right = 0

    if not curr_bubble:
        prepare_bubbles()

    if fire:
        process_collision()

    if curr_fire_count == 0:
        drop_wall()

    if not bubble_group:
        game_result = "Mission Complete"
        is_game_over = True
    elif get_lowest_bubble_bottom() > len(map) * CELL_SIZE:
        game_result = "Game Over"
        is_game_over = True
        change_bubble_image(bubble_images[-1]) # -1: last

    screen.blit(background, (0, 0))
    screen.blit(wall, (0, wall_height - screen_height)) # can't see at first

    # bubble_group.draw(screen) # The func is group's. Annotating so that I can add codes in it like the code below
    draw_bubbles()
    # pointer.rotate(to_angle) 
    pointer.rotate(to_angle_left + to_angle_right) # it's better than the code above
    pointer.draw(screen) # AttributeError: 'Pointer' object has no attribute 'draw' -> solution: Define draw method in pointer class
    if curr_bubble:
        if fire:
            curr_bubble.move()
        curr_bubble.draw(screen) # AttributeError : When an object is in a variable, just go to the class[object] and code the method.

    if next_bubble:
        next_bubble.draw(screen)

    if is_game_over:
        display_game_over()
        running = False
        
    pygame.display.update()

pygame.time.delay(2000)
pygame.quit()
import dac
import pygame
import math
import keymap

def grid(window, rows, cols, size):
  x = 0 
  y = 0
  for i in range(rows):
    x += size
    y += size
    pygame.draw.line(window, (0,0,0), (x,0), (x,size*rows))
    pygame.draw.line(window, (0,0,0), (0,y), (size*cols,y))

def circ(window, rows, cols, size):
  x = 0 
  y = 0
  RADIUS = 80
  for i in range(rows):
    for j in range(cols):
      mag = math.sqrt((i - (RADIUS+1))**2 + (j-(RADIUS + 1))**2)  
      if mag > RADIUS:
        pygame.draw.rect(window, (178, 190, 181), (x,y,size,size))
      y += size
    x += size
    y=0

def cursor(window, state, size):
  pygame.draw.rect(window, (255, 0, 0), (state.p.x*size,state.p.y*size,size,size))

def redraw(window, rows, cols, size,state):
  #window.fill((255,255,255))
  #circ(window, rows, cols, size)
  grid(window, rows, cols, size)
  cursor(window, state, size)
  pygame.display.update()


def update_pos(state,buttons):
  socd_type = 0
  dac_type = 2
  if socd_type == 0:
    dac.second_ip_no_reac(state,buttons)
  else:
    dac.neutral_reac(state,buttons)
  if dac_type == 0:
    dac.box_dac(state,buttons)
  elif dac_type == 1:
    dac.box_travel_time(state,buttons)
  else:
    dac.analog_press(state,buttons)
  pass
  
def main():
  pygame.init()
  NUM_ROWS = 163
  NUM_COLS = 163
  SCALING = 6
  CENTER = ((NUM_ROWS // 2) )
  x = CENTER
  y = CENTER
  window = pygame.display.set_mode((SCALING*NUM_ROWS,SCALING*NUM_COLS))
  bg = pygame.image.load("img/gridless.png")
  s = dac.State(x,y)
  b = dac.Btn()
  running = True
  while running:
    keys = pygame.key.get_pressed()
    b.read(keys[keymap.UP],keys[keymap.DOWN],keys[keymap.LEFT],keys[keymap.RIGHT],keys[keymap.SLOW],
      keys[keymap.HOLD],keys[keymap.NOTCH],keys[keymap.C_UP],keys[keymap.C_DOWN],keys[keymap.C_LEFT],
      keys[keymap.C_RIGHT],keys[keymap.B],keys[keymap.L],keys[keymap.R])
    window.blit(bg, (0, 0))
    update_pos(s,b)
    redraw(window,NUM_ROWS,NUM_COLS,SCALING,s)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        #pygame.image.save( window, 'img/window.png' )
        pygame.quit()
        running = False
      elif event.type == pygame.KEYDOWN:
        if event.key == keymap.QUIT:
            pygame.quit()
            running = False

if __name__ == "__main__":
  main()

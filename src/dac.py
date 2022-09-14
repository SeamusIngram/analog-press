import pygame
import math

class Point():
  def __init__(self,x,y):
    self.x = x
    self.y = y

  def set(self,x,y):
    self.x = x
    self.y = y

  #offsets
  def mag(self):
    return math.sqrt((self.x-81)**2+(self.y-81)**2)

  def ang(self):
      return math.atan2(self.y-81,self.x-81)
      
  # finds the region of the current position. There are 9. 4 cardinals, 4 diagonals and the center
  # center is -1 (to not interfere with calculations of adjacency)
  #  right is 1, and all other regions are ordered in a counter-clockwise fashion (e.g. up-right is 2, etc.)
  def get_region(self):
    # Offset
    x = self.x - 81
    y = self.y - 81
    if x >= 23:
      if y >= 23:
        region = 8
      elif y >= -22:
        region = 1
      else:
        region = 2
    elif x >= -22:
      if y >= 23:
        region = 7
      elif y >= -22:
        region = -1
      else:
        region = 3
    else:
      if y >= 23:
        region = 6
      elif y >= -22:
        region = 5
      else:
        region = 4
    return region

class Btn ():
  def __init__(self):
    self.up = False
    self.down = False
    self.left = False
    self.right = False
    self.slow = False
    self.hold = False
    self.notch = False
    self.c_up = False
    self.c_down = False
    self.c_left = False
    self.c_right= False
    self.B = False
    self.l = False
    self.r = False
    
  def read(self,up,down,left,right,slow,hold,notch,c_up,c_down,c_left,c_right,B,l,r):
    self.up = up
    self.down = down
    self.left = left
    self.right = right
    self.slow = slow
    self.hold = hold
    self.notch = notch
    self.c_up = c_up
    self.c_down = c_down
    self.c_left = c_left
    self.c_right= c_right
    self.B = B
    self.l = l
    self.r = r

class State():
  def __init__(self,x,y):
    self.p = Point(x,y)
    self.t = pygame.time.get_ticks()
    self.reset_hold = True
    
    self.up_pressed = False
    self.down_pressed = False
    self.left_pressed = False
    self.right_pressed = False

    self.forbid_up = False
    self.forbid_down = False
    self.forbid_left = False
    self.forbid_right = False

    self.dx_accum = 0
    self.dy_accum = 0

def second_ip_no_reac(state,buttons):
  if (state.left_pressed and buttons.left and buttons.right and not state.right_pressed):
     state.forbid_left = True
  if (state.right_pressed and buttons.left and buttons.right and  not state.left_pressed):
     state.forbid_right = True
  if (state.up_pressed and buttons.up and buttons.down and not state.down_pressed):
     state.forbid_up = True
  if (state.down_pressed and buttons.up and buttons.down and not state.up_pressed):
     state.forbid_down = True

  if not buttons.left:
     state.forbid_left=False
  if (not buttons.right):
      state.forbid_right = False
  if (not buttons.up):
     state.forbid_up = False
  if (not buttons.down):
     state.forbid_down = False

  state.left_pressed = buttons.left
  state.right_pressed = buttons.right
  state.up_pressed = buttons.up
  state.down_pressed = buttons.down

  if state.forbid_left:
     buttons.left = False
  if state.forbid_right:
     buttons.right = False
  if state.forbid_up:
     buttons.up = False
  if state.forbid_down:
     buttons.down = False

def neutral_reac(state,buttons):
  if buttons.left and buttons.right:
    buttons.left = False
    buttons.right = False
  if buttons.up and buttons.down:
    buttons.up = False
    buttons.down = False


def analog_press(state,buttons):
  t = pygame.time.get_ticks()
  degree_sign = u'\N{DEGREE SIGN}'
  # adjust velocities for balance!
  VEL_FAST = 5
  VEL_SLOW = .2
  VEL_RETURN = .5
  VEL_ROLL = 1

  r = state.p.mag()
  target_p = target(buttons)
  current_region = state.p.get_region()
  target_region = target_p.get_region()
  adjacent_region = True if abs(target_region-current_region) <= 1 or target_region + current_region == 9 else False
  # if on rim, and travelling to an adjacent region, roll the stick along gates instead of following a straight path
  roll_stick = True if r >= 75 and adjacent_region else False
  no_pressed =  not buttons.up and  not buttons.down and not buttons.left and not buttons.right

  if no_pressed:
    v = VEL_RETURN
  elif buttons.slow:
    v = VEL_SLOW
  elif roll_stick:
    v =VEL_ROLL
  else:
    v = VEL_FAST
  dt = t - state.t
  d = v*dt

  # reset the hold duration, to know if the button was let go  
  if not buttons.hold:
    state.reset_hold = True
  # check if all directions were let go
  no_pressed =  not buttons.up and  not buttons.down and not buttons.left and not buttons.right
  # hold current coordinate
  if buttons.hold:
   # so long as at least one button is pressed, and the hold has been released since last hold
    if not no_pressed and state.reset_hold:
      xy = Point(state.p.x, state.p.y)
    else:
      # When no more buttons are pressed, regardless of if hold is still applied, the stick will return to neutral
      target_p = Point(81,81)
      d = VEL_RETURN*dt
      theta = math.atan2(target_p.y-state.p.y,target_p.x-state.p.x)
      dx = d*math.cos(theta) if int(state.p.x) != int(target_p.x) else 0
      dy = d*math.sin(theta)
      xy = quantize(dx,dy,target_p.x,target_p.y,state)
      # Until you let go of hold, the stick will be stuck in neutral
      state.reset_hold = False


  elif roll_stick:
    # 2pi cancels: theta/(2pi radians) = d/(2piR)
    angle_change = d/(80)
    current_angle = state.p.ang()
    counter_clockwise = direction_of_change(state.p,current_region,target_p)
    # logic flipped here because up is negative 
    new_angle = current_angle - angle_change if counter_clockwise else current_angle + angle_change
    if new_angle > math.pi:
      new_angle = new_angle - 2*math.pi
    elif new_angle < -1*math.pi:
      new_angle = new_angle + 2*math.pi
    # notch
    if buttons.notch and current_region%2 == 0 and target_region%2 == 1:
      # targetting a vertical notch
      if ((current_region == 2 or current_region == 4) and target_region == 3) or ((current_region == 6 or current_region == 8) and target_region == 7):
        notch_p = region_coords(current_region,Point(31,73))
      else:
        notch_p = region_coords(current_region,Point(73,31))
      target_angle_change = angle_to_notch(state.p,notch_p)
      # either travel towards notch, or clamp to notch value if it would overshoot
      if angle_change >= abs(target_angle_change) or state.p.x == notch_p.x or state.p.y == notch_p.y:
        xy = Point(notch_p.x,notch_p.y)
      else:
        xy = roll_to_new_point(state,new_angle,current_angle)
    # shield drop
    elif (buttons.l or buttons.r) and target_region%2 == 0 and state.p.y<target_p.y:
      notch_p = region_coords(target_region,Point(56,55))
      target_angle_change = angle_to_notch(state.p,notch_p)
      if angle_change >= abs(target_angle_change) or state.p.x == notch_p.x or state.p.y == notch_p.y:
        xy = Point(notch_p.x,notch_p.y)
      else:
        xy = roll_to_new_point(state,new_angle,current_angle)
    # rolling to gate
    else:
      target_angle_change = angle_to_notch(state.p,target_p)
      if angle_change >= abs(target_angle_change) or state.p.x == target_p.x or state.p.y == target_p.y:
        xy = Point(target_p.x,target_p.y)
      else:
        xy = roll_to_new_point(state,new_angle,current_angle)
  # straight line behaviour
  else:
    # find path between start and end
    theta = math.atan2(target_p.y-state.p.y,target_p.x-state.p.x)
    # cos(0) = 1, so if theta is 0 because you're already at the correct point we want dx to be 0, not d
    dx = d*math.cos(theta) if int(state.p.x) != int(target_p.x) else 0
    dy = d*math.sin(theta)
    xy = quantize(dx,dy,target_p.x,target_p.y,state)
    # stay within bound of the stick circle. Don't forget offset
    if xy.mag()>80:
      xy.set(target_p.x, target_p.y)
  state.p.set(xy.x,xy.y)
  theta_output = round(math.degrees(xy.ang()),1)
  print(f'{round((xy.x-81)/80,4)},{round((xy.y-81)/80,4)} {theta_output}{degree_sign}')
  state.t = pygame.time.get_ticks()

# find the correct target coordinate, based on buttons pressed
def target(buttons):
  # NOTE: the origin stars in the top right, so down is +y, and right is +x 
  offset = 81
  if buttons.up and buttons.left:
    p = Point(-56+offset,-56+offset)
  elif buttons.up and buttons.right:
    p = Point(56+offset,-56+offset)
  elif buttons.down and buttons.left:
    p = Point(-56+offset,56+offset)
  elif buttons.down and buttons.right:
    p = Point(56+offset,56+offset)
  elif buttons.up:
    p = Point(0+offset,-80+offset)
  elif buttons.left:
    p = Point(-80+offset,0+offset)
  elif buttons.down:
    p = Point(0+offset,80+offset)
  elif buttons.right:
    p = Point(80+offset,0+offset)
  else:
    p = Point(0+offset,0+offset)
  # NOTE: there is an offset because pygame grid is always positive
  return p

# Finds which direction around a circle the target is from the current position
# offset
def direction_of_change(p,region,target_p):
  offset = 81
  x = p.x - offset
  y = p.y - offset
  target_x = target_p.x - offset
  target_y = target_p.y - offset
  if region == 1 or region == 2 or region == 8:
    counter_clockwise = True if y > target_y else False
  elif region == 4 or region == 5 or region == 6:
    counter_clockwise = True if y < target_y else False
  elif region == 3:
    counter_clockwise = True if x > target_x else False
  else:
    counter_clockwise = True if x < target_x else False
  return counter_clockwise

# converts a diagonal coordinate to the correct signs. x and y
# make sure up is negative y in pygame!
def region_coords(region,p):
  offset = 81
  if region == 2:
    p_return = Point(abs(p.x)+offset,-1*abs(p.y)+offset)
  if region == 4:
    p_return = Point(-1*abs(p.x)+offset,-1*abs(p.y)+offset)
  if region == 6:
    p_return = Point(-1*abs(p.x)+offset,abs(p.y)+offset)
  if region == 8:
    p_return = Point(abs(p.x)+offset,abs(p.y)+offset)
  return p_return
  
# Finds angle between two points on a circle
# offset
def angle_to_notch(p,target):
  offset = 81
  x = p.x - offset
  y = p.y - offset
  target_x = target.x - offset
  target_y = target.y - offset
  if (x == 0 and target_x == 0) or (y==0 and target_y==0):
    theta = 0
  else:
    theta = 2*math.asin(math.sqrt((x-target_x)**2+(y-target_y)**2)/(2*80))
  return theta

# Take the distance travelled from the current point, and generate a new point that is an actual coordinate
# If dx or dy are ever less than a full step, don't move the point, but accumulate values until finally a full step can be taken
def quantize(dx,dy,tx,ty,state):
  adjusted = False
  if abs(dx) > 0 and abs(dx) < 1:
    state.dx_accum += dx
  if abs(dy) > 0 and abs(dy) < 1:
    state.dy_accum += dy
  if abs(state.dx_accum) > 1:
    x=state.p.x+math.copysign(math.floor(abs(state.dx_accum)),state.dx_accum)
    state.dx_accum = 0
    adjusted = True
  else:
    adjust_x = tx-state.p.x if abs(dx) > abs(tx-state.p.x) else dx
    x= state.p.x+math.copysign(math.floor(abs(adjust_x)),adjust_x)
    if math.copysign(math.floor(abs(adjust_x)),adjust_x) > 0:
      adjusted = True
  if abs(state.dy_accum) > 1:
    y=state.p.y+math.copysign(math.floor(abs(state.dy_accum)),state.dy_accum)
    state.dy_accum = 0
    adjusted = True
  else:
    adjust_y = ty-state.p.y if abs(dy) > abs(ty-state.p.y) else dy 
    y= math.copysign(math.floor(abs(adjust_y)),adjust_y)+state.p.y
    if math.copysign(math.floor(abs(adjust_y)),adjust_y) > 0:
      adjusted = True
  p = Point(x,y)
  # Adjust inwards if overshoot occurs
  if adjusted:
    if p.mag()>80:
      result_angle = p.ang()
      if abs(result_angle)>math.pi/4 and abs(result_angle) < 3*math.pi/4:
        p.y = p.y - math.copysign(1,p.y-82)
      else:
        p.x = p.x - math.copysign(1,p.x-82) 
  return p

# roll along the rim a specified angle to the next point
def roll_to_new_point(state,new_angle,current_angle):
  target_x = math.cos(new_angle) 
  target_y = math.sin(new_angle)
  dx = 80*(math.cos(new_angle) - math.cos(current_angle))
  dy = 80*(math.sin(new_angle) - math.sin(current_angle))
  p = quantize(dx,dy,target_x,target_y,state)
  return p

# Arte's Melee_F1 DAC converted to python
def box_dac(state,buttons):
  p = box_coords(buttons)
  x = p.x
  y = p.y
  theta = round(math.degrees(math.atan2(y,x)),1)
  degree_sign = u'\N{DEGREE SIGN}'
  print(f'{x},{y} {theta}{degree_sign}')
  x = x*80 + 81
  y = y*80 + 81
  state.p.x = x
  state.p.y = y

def box_travel_time(state,buttons):
  t = pygame.time.get_ticks()
  target_p = box_coords(buttons)
  target_p.x = target_p.x*80 + 81
  target_p.y = target_p.y*80 + 81
  VEL_TRAVEL = 3
  v = VEL_TRAVEL
  dt = t - state.t
  d = v*dt
  theta = math.atan2(target_p.y-state.p.y,target_p.x-state.p.x)
  # cos(0) = 1, so if theta is 0 because you're already at the correct point we want dx to be 0, not d
  dx = d*math.cos(theta) if int(state.p.x) != int(target_p.x) else 0
  dy = d*math.sin(theta)

  xy = quantize(dx,dy,target_p.x,target_p.y,state)
  # stay within bound of the stick circle. Don't forget offset
  if xy.mag()>81:
    xy.set(target_p.x, target_p.y)
  state.p.set(xy.x,xy.y)
  theta_output = round(math.degrees(xy.ang()),1)
  degree_sign = u'\N{DEGREE SIGN}'
  print(f'{round((xy.x-81)/80,4)},{round((xy.y-81)/80,4)} {theta_output}{degree_sign}')
  state.t = pygame.time.get_ticks()

def box_coords(buttons):
  vertical = buttons.up or buttons.down
  read_up = buttons.up
  horizontal = buttons.left or buttons.right
  read_right = buttons.right

  if (vertical and horizontal):
    if (buttons.l or buttons.r):
      if (buttons.notch == buttons.slow):
          x = 0.7
          y = 0.7 if read_up else 0.6875
      elif buttons.notch:
          x = 0.6375
          y = 0.375
      else: 
        x = 0.475 if read_up else 0.5
        y = 0.875 if read_up else 0.85
    elif (buttons.B and (buttons.notch != buttons.slow)):
      if (buttons.notch):
        if (buttons.c_down):
            x = 0.9125
            y = 0.45
        elif (buttons.c_left):
            x = 0.85
            y = 0.525
        elif (buttons.c_up):
            x = 0.7375
            y = 0.5375
        elif (buttons.c_right): 
          x = 0.6375
          y = 0.5375
        else:
            x = 0.9125
            y = 0.3875
      else:
        if (buttons.c_down):
          x = 0.45
          y = 0.875
        elif (buttons.c_left):
          x = 0.525
          y = 0.85
        elif (buttons.c_up):
          x = 0.5875
          y = 0.8
        elif (buttons.c_right):  
          x = 0.5875
          y = 0.7125
        else:
            x = 0.3875
            y = 0.9125
                  
    elif (buttons.notch != buttons.slow):
      if (buttons.notch):
        if (buttons.c_down):
          x = 0.7
          y = 0.3625
        elif (buttons.c_left):
          x = 0.7875
          y = 0.4875
        elif (buttons.c_up):
          x = 0.7
          y = 0.5125
        elif (buttons.c_right):  
          x = 0.6125
          y = 0.525
        else:
            x = 0.7375
            y = 0.3125
      else:
        if (buttons.c_down):
          x = 0.3625
          y = 0.7
        elif (buttons.c_left):
          x = 0.4875
          y = 0.7875
        elif (buttons.c_up):
          x = 0.5125
          y = 0.7
        elif (buttons.c_right):  
          x = 0.6375
          y = 0.7625
        else:
            x = 0.3125
            y = 0.7375
    else: 
      x = 0.7
      y = 0.7

  elif (horizontal):
      if (buttons.notch == buttons.slow):
         x = 1.0
         y = 0.0
      elif (buttons.notch): 
        x = 0.6625
        y = 0.0
      else: 
        x = 1.0 if buttons.B else 0.3375
        y = 0.0

  elif (vertical):
      if (buttons.notch == buttons.slow): 
        x = 0.0
        y = 1.0
      elif (buttons.notch): 
        x = 0.0
        y= 0.5375
      else: 
        x = 0.0
        y = 0.7375

  else:
      x = 0
      y = 0

  if (horizontal and not read_right):
    x =  -1.0*x
  if (vertical and read_up): 
    y = -1.0*y
  return Point(x,y)
  
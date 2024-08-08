import pygame as pg
import math
from threading import Thread
from random import seed, randint
#import numpy as np

#Config variables
threading=False #multithreading
death=True #collision of planets
mass_dim=3 #planet size-to-mass proportion in dimensions
particle_count=250 #max count of planets
G=500000 #Greater this value, weaker overall gravity, can be used as density
drag=0 #space drag...
GRID=100 #size in pixels of background grid side
grid_color=[20,20,30] #rgb color of the grid
HEIGHT=540 #Window Height and Width
WIDTH=960
SIZE=1 #game size proportional to window
RESIZE_CONTENT=True


#Technical variables
dead=[]
new_world=[]
disp=pg.display.set_mode((WIDTH, HEIGHT),pg.RESIZABLE)
clock=pg.time.Clock()
lastid,camera,total_mass=0,0,0
def resize():
  h_prop=HEIGHT/1080
  w_prop=WIDTH/1920
  if RESIZE_CONTENT:prop=min(h_prop,w_prop)
  else:prop=1
  prop*=SIZE
  grid=prop*GRID
  v_grids=int(WIDTH/grid+2)
  h_grids=int(HEIGHT/grid+2)
  win_rad=int(math.hypot(HEIGHT,WIDTH)/2/SIZE)
  globals().update(locals())

resize()


class Planet:   #I was forced to...
  def __init__(self,mass,pos,vel):
    self.setmass(mass)
    self.x,self.y=pos
    self.dx,self.dy=vel
    global lastid
    lastid+=1
    self.id=lastid
    self.r=s256(lastid)
    self.g=s256(lastid+1)
    self.b=s256(lastid+2)

  def set(self,mass,pos,vel):
    self.setmass(mass)
    self.x,self.y=pos
    self.dx,self.dy=vel

  def setmass(self,mass):
    self.mass=mass
    self.size=mass**(1/mass_dim)

def proc(base_n):
  global total_mass,camera
  base=world[base_n]
  for obj_n in range(len(world)):
    if obj_n!=base_n:
      obj=world[obj_n]
      dist=max(math.hypot(obj.x-base.x,obj.y-base.y),0.001)
      if death and base.size+obj.size>dist and (base.mass>obj.mass or base.mass>=obj.mass and base_n<obj_n): #collision!
        dead.append(obj_n) #one of us must die
        for task in ["x","y","dx","dy","r","g","b"]: #combining properties when colliding
          exec("base.{0}=(base.{0}*base.mass+obj.{0}*obj.mass)/(base.mass+obj.mass)".format(task))
        base.setmass(base.mass+obj.mass)
        if camera.id==obj.id:camera=base
      elif obj_n==len(world)-1 and dist>win_rad*10:
        dead.append(obj_n)
        total_mass-=obj.mass
      base.dx+=(obj.x-base.x)*obj.mass/G/dist #zakon
      base.dy+=(obj.y-base.y)*obj.mass/G/dist
  base.dx-=drag*(base.dx**2)*math.copysign(1,base.dx)
  base.dy-=drag*(base.dy**2)*math.copysign(1,base.dy)
  base.x+=base.dx
  base.y+=base.dy
  new_world[base_n]=base
  pg.draw.circle(disp,[base.r,base.g,base.b],[
  (base.x-camera.x)*prop+WIDTH/2,
  (base.y-camera.y)*prop+HEIGHT/2],
  math.ceil(base.size*prop))

def add(mass,pos,vel):
  global total_mass
  total_mass+=mass
  planet=Planet(mass,pos,vel)
  new_world.insert(0,planet)
  return planet

def vec(r,l,x=0,y=0):return ([(math.sin(r)*l)+x,(math.cos(r)*l)+y]) #angle+radius->x+y

def create_particles(count,radius,mass,max_vel):
  for i in range(count):
    seed(None)
    a=randint(0,360)
    add(randint(mass[0],mass[1]),
      vec(a,randint(radius[0],radius[1]),camera.x,camera.y),
      vec(a+math.pi/1,randint(0,max_vel)))

def s256(sid):#8 bit seeded random
  seed(sid)
  return randint(0, 255)

def draw_grid():
  for i in range(v_grids):
    pg.draw.line(disp,grid_color,[i*grid-camera.x%grid,0],[i*grid-camera.x%grid,HEIGHT])
  for i in range(h_grids):
    pg.draw.line(disp,grid_color,[0,i*grid-camera.y%grid],[WIDTH,i*grid-camera.y%grid])


#default planets
#add(50000,[750,500],[0,0])
#add(5000,[1000,500],[0,-4])
#add(500,[1050,500],[0,-4.1])
#add(1000,[500,750],[0,10])
#add(1000,[250,500],[0,-5])
#add(1000,[505,750],[0,0])
camera=add(201,[750,500],[0,0])
while 1:
  world=new_world.copy()
  disp.fill([0, 0, 0])
  draw_grid()
  if threading:
    threads = [Thread(target=proc, args=(i,)) for i in range(len(world))]
    for t in threads:
      t.start()
    for t in threads:
      t.join()
  else:
    for i in range(len(world)):proc(i)
  if len(dead)>0:
    dead.sort(reverse=True)
    for i in dead:
      try:new_world.pop(i)
      except:pass
    dead=[]
  pg.display.update()
  create_particles(particle_count-len(new_world),[win_rad,win_rad*5], [50, 200], 10)
  #new_world[0].set(50000,[750,500],[0,0])
  clock.tick(30)
  for event in pg.event.get():
    if event.type == pg.QUIT:
      pg.quit()
      quit(1488)
    if event.type==pg.VIDEORESIZE:
      WIDTH,HEIGHT=event.w, event.h
      resize()

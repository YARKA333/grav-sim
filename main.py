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
drag=0
grid=100
grid_color=[10,10,15]

#IT LOOKS LIKE CONFIG BUT IT'S NOT
#EDIT AT YOUR OWN RISK
HEIGHT=1080
WIDTH=1920

#Technical variables
dead=[]
new_world=[]
disp=pg.display.set_mode((WIDTH, HEIGHT))
clock=pg.time.Clock()
lastid=0
v_grids=int(WIDTH/grid+1)
h_grids=int(HEIGHT/grid+1)
total_mass=0
camera=1



class Planet():#I was forced to...
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
  global camera
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
        if camera==obj.id:camera=base.id
        if camera==base.id:camera_n=base_n
      elif obj_n==len(world)-1 and dist>10000:
        dead.append(obj_n)
        total_mass-=obj.mass
      base.dx+=(obj.x-base.x)*obj.mass/G/dist #zakon
      base.dy+=(obj.y-base.y)*obj.mass/G/dist
  base.dx-=drag*(base.dx**2)*math.copysign(1,base.dx)
  base.dy-=drag*(base.dy**2)*math.copysign(1,base.dy)
  base.x+=base.dx
  base.y+=base.dy
  new_world[base_n]=base
  pg.draw.circle(disp,[base.r,base.g,base.b], [(base.x-world[-1].x+WIDTH/2),(base.y-world[-1].y+HEIGHT/2)],base.size)

def add(mass,pos,vel):
  global total_mass
  total_mass+=mass
  new_world.insert(0,Planet(mass,pos,vel))#less letters

def vec(r,l,x=0,y=0):return ([(math.sin(r)*l)+x,(math.cos(r)*l)+y]) #angle+radius->x+y

def create_particles(count,radius,mass,max_vel):
  for i in range(count):
    seed(None)
    a=randint(0,360)
    add(randint(mass[0],mass[1]),
      vec(a,randint(100,radius),world[-1].x,world[-1].y),
      vec(a+math.pi/2,randint(0,max_vel)))

def s256(sid):#8 bit seeded random
  seed(sid)
  return randint(0, 255)

def draw_grid():
  for i in range(v_grids):
    pg.draw.line(disp,grid_color,[i*grid-world[-1].x%grid,0],[i*grid-world[-1].x%grid,HEIGHT])
  for i in range(h_grids):
    pg.draw.line(disp,grid_color,[0,i*grid-world[-1].y%grid],[WIDTH,i*grid-world[-1].y%grid])


#default planets
#add(50000,[750,500],[0,0])
#add(5000,[1000,500],[0,-4])
#add(500,[1050,500],[0,-4.1])
#add(1000,[500,750],[0,10])
#add(1000,[250,500],[0,-5])
#add(1000,[505,750],[0,0])
add(201,[750,500],[0,0])
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
  create_particles(particle_count-len(new_world),5000, [50, 200], 10)
  #new_world[0].set(50000,[750,500],[0,0])
  clock.tick(30)
  for event in pg.event.get():
    if event.type == pg.QUIT:
      pg.quit()
      quit(1488)
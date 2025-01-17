# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 17:09:01 2019

@author: Alexandre
"""
import numpy as np 
import matplotlib.pyplot as plt


# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 15:01:15 2019

@author: Alexandre
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 21:10:26 2019

@author: Alexandre
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class particles:
    def __init__(self,m=1.0,npart=10,soft=1,G=1.0,dt=0.1,grid_size=50):
        #initializing partcle settings
        self.opts={}
        self.opts['soft']=soft
        self.opts['n']=npart
        self.opts['G']=G
        self.opts['dt']=dt
        self.opts['grid_size']=grid_size

        self.opts['m']=m
        #random particles generated 
        self.x,self.y=np.random.randint(0, self.opts['grid_size'], size=(2, self.opts['n']))
        #self.m=m
        self.vx=np.double(self.x.tolist())*0
        self.vy=np.double(self.y.tolist())*0
        
        #creating greens function
        xx= np.linspace(0, grid_size-1, grid_size)
        self.kx,self.ky=np.meshgrid(xx,xx)
        kx=self.kx
        ky=self.ky
        
        Gr=1/(1e-13+4*np.pi*((kx)**2+(ky)**2)**(1/2))
        Gr[0,0]=1/(4*np.pi*soft)
        #making the function apply to every corner
        Gr+=np.flip(Gr,0)
        Gr+=np.flip(Gr,1)
        #fourier transform to convolve
        Gr_ft=np.fft.fft2(Gr)
        self.Gr_ft=Gr_ft

        self.energy=0
    def get_grid(self,x,y):
        
        grid_size=self.opts['grid_size']
        #density grid
        #the boundary conditions are represented by the % operator
        #using the closest distance method by rounding the particle location
        A=np.histogram2d((np.round(x)%grid_size).astype(int),(np.round(y)%grid_size).astype(int),bins=grid_size,range=[[0, grid_size], [0, grid_size]])[0]*self.opts['m']
#       Convolving the greens function with the density grid
        Gr_ft=self.Gr_ft
        rho_ft=np.fft.fft2(A)
        conv=Gr_ft*rho_ft
        pot=np.fft.ifft2(conv)
        #making sure the potential is centered with the particle positions
        pot=0.5*(np.roll(pot,1,axis=1)+pot)
        pot=0.5*(np.roll(pot,1,axis=0)+pot)
        

        return A,pot
        
    def power_law_mass(self,x,y):
        """
        Using this function only once to set up the initial grid density
        """
        
        
        grid_size=self.opts['grid_size']
        #density grid
        #the boundary conditions are represented by the % operator
        #using the closest distance method by rounding the particle location
        A=np.histogram2d((np.round(x)%grid_size).astype(int),(np.round(y)%grid_size).astype(int),bins=grid_size,range=[[0, grid_size], [0, grid_size]])[0]*self.opts['m']
#       Convolving the greens function with the density grid
        Gr_ft=self.Gr_ft
        rho_ft=np.fft.fft2(A)
        conv=Gr_ft*rho_ft
        pot=np.fft.ifft2(conv)
        #making sure the potential is centered with the particle positions
        pot=0.5*(np.roll(pot,1,axis=1)+pot)
        pot=0.5*(np.roll(pot,1,axis=0)+pot)
        #getting fourier positions
        kx=self.kx
        ky=self.ky
        k=((kx-grid_size//2)**2+(ky-grid_size//2)**2)**(1/2)
        self.k=k
        #softening
        soft=50
        k[k<soft]=soft
        #adding gaussian random noise
        mult=np.max(abs(rho_ft*1/k**3))
        #attributing a mass of 1/k^3 as specified in question 4
        new_mass=np.fft.ifft2(rho_ft*1/k**3+np.random.rand()*mult)
        #new_mass=np.fft.fftshift(np.fft.ifft(rho_ft*1/k**3*np.random.rand()))
        self.new_mass=new_mass
        
        return abs(new_mass),pot
        
        
    def get_force(self,x,y,pot,A):
        
        
        #taking the gradient of the potential to get the forces
        #multiplying by density matrix
        forcex=-1/2*(np.roll(pot,1,axis=0)-np.roll(pot,-1,axis=0))*A
        forcey=-1/2*(np.roll(pot,1,axis=1)-np.roll(pot,-1,axis=1))*A

        #initializing new x and y positions 
        x_new=np.double(x.tolist())*0
        y_new=np.double(y.tolist())*0
        
        #changing the velocities of each particle by taking the force of each particle and multiplying it by time
        #changing the positions of each particle with the new velocity        
        self.vx+=np.real(forcex[(np.round(x)%self.opts['grid_size']).astype(int),(np.round(y)%self.opts['grid_size']).astype(int)])*self.opts['dt']
        x_new=x+self.vx*self.opts['dt']
        self.vy+=np.real(forcey[(np.round(x)%self.opts['grid_size']).astype(int),(np.round(y)%self.opts['grid_size']).astype(int)])*self.opts['dt']
        y_new=y+self.vy*self.opts['dt']        
        m=self.opts['m']
        #defining the total energy
        self.energy=1/2*np.sum(self.vx**2+self.vy**2)*m+np.sum(pot)/2

        return x_new,y_new

        
if __name__=='__main__':
    
    #defining the parameters
    n=100000
    grid_size=500
    dt=0.1
    #max time
    time=100
    #creating the particle
    part=particles(m=1,npart=n,dt=dt,grid_size=grid_size)
    #getting density and potential
    A,pot=part.power_law_mass(part.x,part.y)
    #getting new positions
    x_new,y_new=part.get_force(part.x,part.y,pot,A)

    """
    The commented code in the section below is to provide the videos.

    
    """
    
    grid=np.zeros([int(time//dt)+1,grid_size,grid_size])
    
    #initialize the count
    count=0
    #initilize energy array
    energy=np.zeros(int(time//dt)+1)
    
    #for each time step
    for i in np.arange(0,time,part.opts['dt']):
        
        
        A_new,pot=part.get_grid(x_new,y_new)
        x_new,y_new=part.get_force(x_new,y_new,pot,A_new)
        
        
        grid[count]=A_new
        energy[count]=np.real(part.energy)
        
        plt.clf()
        plt.imshow(abs(A_new))
        plt.pause(0.0001)
        
        count+=1
        
        
    plt.figure()
    plt.xlabel("time steps")
    plt.ylabel("Energy")
    plt.plot(energy)


#    fig, ax = plt.subplots(figsize=(8, 6))
#    cax = ax.imshow(grid[0])
#    
#    cb = fig.colorbar(cax)
#    
#    def animate(i):
#          
#        cax.set_array(grid[i])
#    
#        
#    anim = FuncAnimation(fig, animate, interval=40, frames=grid.shape[0], repeat=True,blit=False,save_count=grid.shape[0])
#    
    #anim.save("power_spec_particles.gif")

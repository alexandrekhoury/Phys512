# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 14:13:26 2019

@author: Alexandre
"""

import numpy as np
import camb
from matplotlib import pyplot as plt
import time


def get_spectrum(pars,lmax):
    #print('pars are ',pars)
    H0=pars[0]
    ombh2=pars[1]
    omch2=pars[2]
    tau=pars[3]
    As=pars[4]
    ns=pars[5]
    pars=camb.CAMBparams()
    pars.set_cosmology(H0=H0,ombh2=ombh2,omch2=omch2,mnu=0.06,omk=0,tau=tau)
    pars.InitPower.set_params(As=As,ns=ns,r=0)
    pars.set_for_lmax(lmax,lens_potential_accuracy=0)
    results=camb.get_results(pars)
    powers=results.get_cmb_power_spectra(pars,CMB_unit='muK')
    cmb=powers['total']
    tt=cmb[:,0]    #you could return the full power spectrum here if you wanted to do say EE
    return tt


plt.ion()

wmap=np.loadtxt('wmap_tt_spectrum_9yr_v5.txt')
pars=np.asarray([65,0.02,0.1,0.05,2e-9,0.96])

cmb=get_spectrum(pars,wmap[:,0].size)[2:]


#function that returns the chisquare given the model, data and variance
def get_chisquare(model,data,err):
    chisq=np.sum((model-data)**2/err**2)
    return chisq


datax,datay,err=[wmap[:,0],wmap[:,1],wmap[:,2]]


print("The chisquare for this model is: " + str(get_chisquare(cmb,datay,err)))


#plt.clf();
#plt.errorbar(wmap[:,0],wmap[:,1],wmap[:,2],fmt='*')
#plt.plot(wmap[:,0],wmap[:,1],'.')


#plt.plot(cmb)
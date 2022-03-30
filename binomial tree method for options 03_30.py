#Program to for binomial tree method of option valuation
#We will value the asset S then work backwards through a binary tree to calculate
#the value of an option at time t=0 where S is the underlying asset for the option.
#Will deal with two cases on how to value the underlying asset price with discretised random walks?
#This is because an extra assumption is needed to solve the system that is produced
#We will use 3FIN notes where the continuous random walk is turned to a discrete random walk which is justified in the notes.
#Case values u,d,p calculated by expected values and variance 

#IMPORTANT TO-DOs:
# round consistently throughout!!!

import math
import numpy as np
import sympy as sym

class asset():
    def __init__(self,delt,T,r,sigma,case,S_0):
        self.delt = float(delt) #each timestep difference so we want M*delt = T
        self.T = float(T) #expiry time i.e. 5 years
        self.r = float(r) #interest rate
        self.sigma = float(sigma)
        self.case = int(case) 
        self.M = int(self.T/self.delt) #max timesteps, need to re check this as integer???
        self.S_0 = float(S_0) #the current value of the asset


        self.print_initial_conditions()
        self.get_case()
        

    def case1(self): 
        #this is the case for ud = 1, where u is an up jump and d is a down jump in the tree, we use this to work out p

        A = 0.5*(math.exp(-self.r*self.delt)+math.exp((self.r+self.sigma**2)*self.delt))
        self.d = A - math.sqrt(A**2-1)
        self.u = A + math.sqrt(A**2-1)
        self.p = (math.exp(self.r*self.delt)-self.d)/(self.u-self.d)
        self.print_discrete_variables(A)

    def case2(self): 
        #this is case for p = 0.5

        A = 0 
        self.p = 0.5
        self.d = math.exp(self.r*self.delt)*(1-math.sqrt(math.exp(self.delt*self.sigma**2)-1)) 
        self.u = math.exp(self.r*self.delt)*(1+math.sqrt(math.exp(self.delt*self.sigma**2)-1))
        self.print_discrete_variables(A) 

    def get_case(self):
        #Assigns the case to the asset to ensure the correct type of tree is calculated
        if self.case == 1:
            self.case1()
        else: 
            self.case2()    


    def asset_tree(self):
        #method to build the tree of prices for the asset
        #we will use variable n to count the number of up jumps of the asset 

        self.S = [] #list of all predicted asset values for each timestep
                    #Use the first index as the timestep m=0,1,...,M and the second index(later) for the amount of up jumps at that timestep
                    #e.g. timestep 3 has entries of 3 up jumps S[3][3], 2 up jumps S[3][2], 1 up jump S[3][1] and 0 up jumps S[3][0] 

        #self.S[0].append(self.S_0) #so at timestep 0 (first index) and 0 up jumps (second index) the value is S_0, the current value of the asset

        for m in range(0,self.M+1):
            step_list = [] # to store all values on current timestep
            for n in range(0,m+1):
                step_list.append((self.d**(m-n))*(self.u**n)*self.S_0) #asset price/value at timestep m with n up jumps. Appended from 0 to n in the list
            self.S.append(step_list)
        self.print_tree()        

    def print_initial_conditions(self):
        #to check initial conditions entered correctly
        print("delta_t = {}".format(self.delt))
        print("Expiry time T = {}".format(self.T))
        print("Interest rate is {}".format(self.r))
        print("Volatility (sigma) is {}".format(self.sigma))
        print("Case: {}".format(self.case))
        print("Total timesteps M = {}".format(self.M))
        print("Current asset price = {}".format(self.S_0))

    def print_discrete_variables(self,A):
        #to ensure the variables are calculated correctly
        print("Value of A = {}".format(A))
        print("value of d = {}".format(self.d))
        print("Value of u = {}".format(self.u))
        print("Value of p = {}".format(self.p))

    def print_tree(self):
        #Used to print the entire binomial tree of asset values at each timestep.

        for m in range(0,self.M+1):
            print("Values at timestep {} are:".format(m))
            for n in range(0,m+1):
                print("S_{}_{} = {}".format(m,n,self.S[m][n]))   


share = asset(0.1,2,0.01,1,1,5)

share.asset_tree()
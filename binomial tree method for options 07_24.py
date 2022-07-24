#Program to for binomial tree method of option valuation
#We will value the asset S then work backwards through a binary tree to calculate
#the value of an option at time t=0 where S is the underlying asset for the option.
#Will deal with two cases on how to value the underlying asset price with discretised random walks?
#This is because an extra assumption is needed to solve the system that is produced
#We will use 3FIN notes where the continuous random walk is turned to a discrete random walk which is justified in the notes.
#Case values u,d,p calculated by expected values and variance 

#IMPORTANT TO-DOs:
# round consistently throughout!!!
# implement class and methods for Euro calls and puts
# subclass for American calls and puts
# sort for underlying asset which pays continuous dividend D_0

import math
import numpy as np
import sympy as sym

class asset():
    def __init__(self,delt,T,r,sigma,case,S_0):
        self.delt = float(delt) #each timestep difference so we want M*delt = T
        self.T = float(T) #expiry time i.e. 5 years
        self.r = float(r) #interest rate
        self.sigma = float(sigma) #standard deviation 
        self.case = int(case) #this refers to the different methods to calculate probabilities
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


#Class for the option on the underlying asset, will use calls, puts both euro and american 
class Option():


    def __init__(self,asset,type,strike_price):

        self.type = type # this will be the type of option e.g. call or put.
        self.E = float(strike_price)
        self.T = asset.T #expiry time   
        self.M = asset.M #number of timesteps
        self.p = asset.p #probability from the asset class
        self.r = asset.r #gets interest rate
        self.delt = asset.delt #delta_t timestep difference
        self.asset_tree = asset.S

        self.print_option_conditions() 
        self.set_type() #moves our option into the required subclass 

        return


    def print_option_conditions(self):
        #will print the initial conditions of the option.
        print("This is a {} option".format(self.type))
        print("Strike price is: {}".format(self.E))
        print("Expiry time is {}".format(self.T))
        print("Probability used is p={}".format(self.p))
        print("Interest rate r = {}".format(self.r))

    def set_type(self):
        #here we immediately set the option type to move straight into the required subclass
        if self.type == "Call":
            Call(self,self.E)
        elif self.type == "Put":
            Put(self,self.E)
        elif self.type == "C or N":
            K = float(input("What is the payoff K for this option: "))
            style = input("Is this option a Call or Put? ") #as this option can take either form
            Cash_or_nothing(self,self.E,K,style)
        elif self.type == "A or N":
            style = input("Is this option a Call or Put? ") #as this option can take either form
            Asset_or_nothing(self,self.E,style)
        elif self.type == "Call on call":
            Call_on_call(self, self.E)    
        elif self.type == "Call on put":
            Call_on_put(self, self.E)  
        elif self.type == "Put on call":
            Put_on_call(self, self.E)      
        else: 
            return        


class Call(Option):

    def __init__(self,asset,E):
        self.type = "Call"
        self.E = float(E)
        self.T = asset.T #expiry time   
        self.M = asset.M #number of timesteps
        self.p = asset.p #probability from the asset class
        self.r = asset.r #interest rate
        self.delt = asset.delt #timestep difference
        self.asset_tree = asset.asset_tree
        self.Am = input("Is the call American? (Y or N): ")
        print(self.Am)
        self.print_option_conditions()
        self.Value_tree_method()

        return

    def payoff(self,m,n): 
        #gets the payoff for the call, this will be used at top/max timestep M in the tree for euro call and at each step for american calls
        #print(self.asset_tree[m][n])
        V = max(self.asset_tree[m][n]-self.E,0)
        return V  

    def step_value(self,m,n):
        #gets value of the option at a given timestep for each number of upjumps within that timestep
        
        correction_factor = math.exp(-self.r*self.delt) #time value of money factor from the asset

        value = correction_factor * (self.p * self.V_tree[m-1][n+1] + (1-self.p) * self.V_tree[m-1][n])       

        if self.Am == "Y":
            payoff = self.payoff(self.M-m,n)
            print(payoff,value)
            return max(payoff,value)
        else:
             return value  

    def Value_tree_method(self):
        
        self.V_tree = [] #list for the option values V at each timestep
        step_list = [] # loop below sorts out the option values at the final timestep
        for n in range(0,self.M+1):
            step_list.append(self.payoff(self.M,n))
        self.V_tree.append(step_list)

        #print(self.V_tree)
        
        #this loop calculates each time step from the final timestep backwards to the current time and the current value of the option
        #Note this runs the opposite way to the asset tree and the upjump counter reflects this
        for m in range(1,self.M+1):
            step_list = []
            for n in range(0,self.M-m+1):
                step_list.append(self.step_value(m,n))
            self.V_tree.append(step_list)   
            #print(self.V_tree[m]) 

        self.print_Value_tree()        

        return

    def print_Value_tree(self):
        #Used to print the entire binomial tree of asset values at each timestep.

        for m in range(0,self.M+1):
            print("Values at timestep {} are:".format(self.M-m))
            for n in range(0,self.M-m+1):
                print("V_{}_{} = {}".format(self.M-m,n,self.V_tree[m][n]))



class Put(Option):

    def __init__(self,asset,E):
        self.type = "Put"
        self.E = float(E)
        self.T = asset.T #expiry time   
        self.M = asset.M #number of timesteps
        self.p = asset.p #probability from the asset class
        self.r = asset.r #interest rate
        self.delt = asset.delt #timestep difference
        self.asset_tree = asset.asset_tree
        self.Am = input("Is the put American? (Y or N): ")
        print(self.Am)
        self.print_option_conditions()
        self.Value_tree_method()

        return

    def payoff(self,m,n): 
        #gets the payoff for the put, this will be used at top/max timestep M in the tree for euro call and at each step for american calls
        #print(self.asset_tree[m][n])
        V = max(self.E-self.asset_tree[m][n],0)
        return V  

    def step_value(self,m,n):
        #gets value of the option at a given timestep for each number of upjumps within that timestep
        
        correction_factor = math.exp(-self.r*self.delt) #time value of money factor from the asset

        value = correction_factor * (self.p * self.V_tree[m-1][n+1] + (1-self.p) * self.V_tree[m-1][n])       

        if self.Am == "Y":
            payoff = self.payoff(self.M-m,n)
            print(payoff,value)
            return max(payoff,value)
        else:
             return value  

    def Value_tree_method(self):
        
        self.V_tree = [] #list for the option values V at each timestep
        step_list = [] # loop below sorts out the option values at the final timestep
        for n in range(0,self.M+1):
            step_list.append(self.payoff(self.M,n))
        self.V_tree.append(step_list)

        #print(self.V_tree)
        
        #this loop calculates each time step from the final timestep backwards to the current time and the current value of the option
        #Note this runs the opposite way to the asset tree and the upjump counter reflects this
        for m in range(1,self.M+1):
            step_list = []
            for n in range(0,self.M-m+1):
                step_list.append(self.step_value(m,n))
            self.V_tree.append(step_list)   
            #print(self.V_tree[m]) 

        self.print_Value_tree()        

        return

    def print_Value_tree(self):
        #Used to print the entire binomial tree of asset values at each timestep.

        for m in range(0,self.M+1):
            print("Values at timestep {} are:".format(self.M-m))
            for n in range(0,self.M-m+1):
                print("V_{}_{} = {}".format(self.M-m,n,self.V_tree[m][n]))


class Cash_or_nothing(Option):
#pays out cash K at expiry if underlying asset price lies above/below strike price E at expiry.
#has Euro and American version of calls/puts
    def __init__(self,asset,E,K,style):
        self.type = style #A call or a put
        self.E = float(E) #strike price
        self.T = asset.T #expiry time   
        self.M = asset.M #number of timesteps
        self.p = asset.p #probability from the asset class
        self.r = asset.r #interest rate
        self.delt = asset.delt #timestep difference
        self.K = K #payoff at expiry
        self.asset_tree = asset.asset_tree
        self.Am = input("Is the option American? (Y or N): ")
        print(self.Am)
        self.print_option_conditions()
        self.Value_tree_method()

        return    

    def payoff(self,m,n):
        #gets the payoff of the cash or nothing option, deals with both the call and put variation

        if self.type == "Call":
            if self.asset_tree[m][n] > self.E:
                return self.K
            else: return 0
        elif self.type == "Put":
            if self.asset_tree[m][n] < self.E:
                return self.K
            else: return 0            

        return 


    def step_value(self,m,n):
        #gets value of the option at a given timestep for each number of upjumps within that timestep
        
        correction_factor = math.exp(-self.r*self.delt) #time value of money factor from the asset

        value = correction_factor * (self.p * self.V_tree[m-1][n+1] + (1-self.p) * self.V_tree[m-1][n])       

        if self.Am == "Y":
            payoff = self.payoff(self.M-m,n)
            print(payoff,value)
            return max(payoff,value)
        else:
             return value 


    def Value_tree_method(self):
        
        self.V_tree = [] #list for the option values V at each timestep
        step_list = [] # loop below sorts out the option values at the final timestep
        for n in range(0,self.M+1):
            step_list.append(self.payoff(self.M,n))
        self.V_tree.append(step_list)

        #print(self.V_tree)
        
        #this loop calculates each time step from the final timestep backwards to the current time and the current value of the option
        #Note this runs the opposite way to the asset tree and the upjump counter reflects this
        for m in range(1,self.M+1):
            step_list = []
            for n in range(0,self.M-m+1):
                step_list.append(self.step_value(m,n))
            self.V_tree.append(step_list)   
            #print(self.V_tree[m]) 

        self.print_Value_tree()        

        return

    def print_Value_tree(self):
        #Used to print the entire binomial tree of asset values at each timestep.

        for m in range(0,self.M+1):
            print("Values at timestep {} are:".format(self.M-m))
            for n in range(0,self.M-m+1):
                print("V_{}_{} = {}".format(self.M-m,n,self.V_tree[m][n])) 


class Asset_or_nothing(Option):
#pays out one unit of the underlying asset at expiry if underlying asset price lies above/below strike price E at expiry.
#has Euro and American version of calls/puts
    def __init__(self,asset,E,style):
        self.type = style #A call or a put
        self.E = float(E) #strike price
        self.T = asset.T #expiry time   
        self.M = asset.M #number of timesteps
        self.p = asset.p #probability from the asset class
        self.r = asset.r #interest rate
        self.delt = asset.delt #timestep difference
        self.asset_tree = asset.asset_tree
        self.Am = input("Is the option American? (Y or N): ")
        print(self.Am)
        self.print_option_conditions()
        self.Value_tree_method()

        return 

    def payoff(self,m,n):
        #gets the payoff of the asset or nothing option, deals with both the call and put variation
        #is just the value of the asset depending on whether the asset price is above/below strike price
        if self.type == "Call":
            if self.asset_tree[m][n] > self.E:
                return self.asset_tree[m][n]
            else: return 0
        elif self.type == "Put":
            if self.asset_tree[m][n] < self.E:
                return self.asset_tree[m][n]
            else: return 0            

        return 


    def step_value(self,m,n):
        #gets value of the option at a given timestep for each number of upjumps within that timestep
        
        correction_factor = math.exp(-self.r*self.delt) #time value of money factor from the asset

        value = correction_factor * (self.p * self.V_tree[m-1][n+1] + (1-self.p) * self.V_tree[m-1][n])       

        if self.Am == "Y":
            payoff = self.payoff(self.M-m,n)
            print(payoff,value)
            return max(payoff,value)
        else:
             return value 


    def Value_tree_method(self):
        
        self.V_tree = [] #list for the option values V at each timestep
        step_list = [] # loop below sorts out the option values at the final timestep
        for n in range(0,self.M+1):
            step_list.append(self.payoff(self.M,n))
        self.V_tree.append(step_list)

        #print(self.V_tree)
        
        #this loop calculates each time step from the final timestep backwards to the current time and the current value of the option
        #Note this runs the opposite way to the asset tree and the upjump counter reflects this
        for m in range(1,self.M+1):
            step_list = []
            for n in range(0,self.M-m+1):
                step_list.append(self.step_value(m,n))
            self.V_tree.append(step_list)   
            #print(self.V_tree[m]) 

        self.print_Value_tree()        

        return

    def print_Value_tree(self):
        #Used to print the entire binomial tree of asset values at each timestep.

        for m in range(0,self.M+1):
            print("Values at timestep {} are:".format(self.M-m))
            for n in range(0,self.M-m+1):
                print("V_{}_{} = {}".format(self.M-m,n,self.V_tree[m][n])) 


class Call_on_call(Option):
    #call on call C1 allows holder to buy a call C2 on an underlying asset at time T1 where C2 has expiry T2
    #we deal with the call C2 firstly then work to value C1 from this 
    def __init__(self,asset,E):
        self.type = "Call on call"
        self.E2 = float(E) #strike price of underlying call C2
        self.T2 = asset.T #expiry time of underlying call C2(comes from the asset tree final time)   
        self.M = asset.M #number of timesteps
        self.p = asset.p #probability from the asset class
        self.r = asset.r #interest rate
        self.delt = asset.delt #timestep difference
        self.asset_tree = asset.asset_tree
        self.Am = "N"
        self.T1 = float(input("Enter expiry of the call C1: "))
        self.E1 = float(input("Enter the strike price of call C1: "))

        self.print_option_conditions()
        self.Value_tree_method()
        self.C1_value_tree()

        return

    def print_option_conditions(self):
        print("Option is a Call C1, with expiry {} and strike price {} on an underlying call C2.".format(self.T1,self.E1))
        print("Where C2 has expiry {} and strike price {} on an underlying asset S".format(self.T2,self.E2))

        return


    def payoff(self,m,n): 
        #gets the payoff for the call, this will be used at top/max timestep M in the tree for euro call and at each step for american calls
        #print(self.asset_tree[m][n])
        V = max(self.asset_tree[m][n]-self.E2,0)
        return V  

    def step_value(self,m,n):
        #gets value of the option at a given timestep for each number of upjumps within that timestep
        
        correction_factor = math.exp(-self.r*self.delt) #time value of money factor from the asset

        value = correction_factor * (self.p * self.V_tree[m-1][n+1] + (1-self.p) * self.V_tree[m-1][n])       

        if self.Am == "Y":
            payoff = self.payoff(self.M-m,n)
            print(payoff,value)
            return max(payoff,value)
        else:
             return value  

    def Value_tree_method(self):
        
        self.V_tree = [] #list for the option values V at each timestep
        step_list = [] # loop below sorts out the option values at the final timestep
        for n in range(0,self.M+1):
            step_list.append(self.payoff(self.M,n))
        self.V_tree.append(step_list)

        #print(self.V_tree)
        
        #this loop calculates each time step from the final timestep backwards to the current time and the current value of the option
        #Note this runs the opposite way to the asset tree and the upjump counter reflects this
        for m in range(1,self.M+1):
            step_list = []
            for n in range(0,self.M-m+1):
                step_list.append(self.step_value(m,n))
            self.V_tree.append(step_list)   
            #print(self.V_tree[m]) 

        self.print_Value_tree()        

        return

    def print_Value_tree(self):
        #Used to print the entire binomial tree of asset values at each timestep.

        for m in range(0,self.M+1):
            print("Values at timestep {} are:".format(self.M-m))
            for n in range(0,self.M-m+1):
                print("V_{}_{} = {}".format(self.M-m,n,self.V_tree[m][n]))

    def C1_value_tree(self):
        #here we move back to T1 which is the expiry of the underlying call C1 to 
        #understand whether to exercise the option and if so find the current value of C1
        #we require the timestep M' which corresponds to the time T1 and will use the already generated C2 tree to get the needed payoff values
        
        self.M = self.T1 / self.delt #this gets the new Mth timestep
        self.M = int(self.M)
        self.temp_tree = [] #this is needed to ensure we can recycle code from above 

        #this sorts out the payoffs at the top of the C1 tree i.e. at time T1, we can the work backwards
        step_list = [] # loop below sorts out the option values at the final timestep
        for n in range(0,self.M+1):
            payoff = max(self.V_tree[self.M][n] - self.E1, 0)
            step_list.append(payoff)
        self.temp_tree.append(step_list)

        self.V_tree = self.temp_tree #ensures we can still use the regular step method by overwriting the current tree

        #this loop calculates each time step from the final timestep backwards to the current time and the current value of the option
        #Note this runs the opposite way to the asset tree and the upjump counter reflects this
        for m in range(1,self.M+1):
            step_list = []
            for n in range(0,self.M-m+1):
                step_list.append(self.step_value(m,n))
            self.V_tree.append(step_list)   
            #print(self.V_tree[m]) 

        self.print_Value_tree()

        return


class Call_on_put(Option):

    #call on put C1 allows holder to buy a put P2 on an underlying asset at time T1 where P2 has expiry T2
    #we deal with the Put P2 firstly then work to value C1 from this 
    def __init__(self,asset,E):
        self.type = "Call on put"
        self.E2 = float(E) #strike price of underlying put P2
        self.T2 = asset.T #expiry time of underlying put P2(comes from the asset tree final time)   
        self.M = asset.M #number of timesteps
        self.p = asset.p #probability from the asset class
        self.r = asset.r #interest rate
        self.delt = asset.delt #timestep difference
        self.asset_tree = asset.asset_tree
        self.Am = "N"
        self.T1 = float(input("Enter expiry of the call C1: "))
        self.E1 = float(input("Enter the strike price of call C1: "))

        self.print_option_conditions()
        self.Value_tree_method()
        self.C1_value_tree()

        return

    def print_option_conditions(self):
        print("Option is a Call C1, with expiry {} and strike price {} on an underlying put P2.".format(self.T1,self.E1))
        print("Where P2 has expiry {} and strike price {} on an underlying asset S".format(self.T2,self.E2))

        return


    def payoff(self,m,n): 
        #gets the payoff for the put P2, this will be used at top/max timestep M in the tree for euro call and at each step for american puts
        #print(self.asset_tree[m][n])
        V = max(self.E2-self.asset_tree[m][n],0)
        return V  

    def step_value(self,m,n):
        #gets value of the option at a given timestep for each number of upjumps within that timestep
        
        correction_factor = math.exp(-self.r*self.delt) #time value of money factor from the asset

        value = correction_factor * (self.p * self.V_tree[m-1][n+1] + (1-self.p) * self.V_tree[m-1][n])       

        if self.Am == "Y":
            payoff = self.payoff(self.M-m,n)
            print(payoff,value)
            return max(payoff,value)
        else:
             return value  

    def Value_tree_method(self):
        
        self.V_tree = [] #list for the option values V at each timestep
        step_list = [] # loop below sorts out the option values at the final timestep
        for n in range(0,self.M+1):
            step_list.append(self.payoff(self.M,n))
        self.V_tree.append(step_list)

        #print(self.V_tree)
        
        #this loop calculates each time step from the final timestep backwards to the current time and the current value of the option
        #Note this runs the opposite way to the asset tree and the upjump counter reflects this
        for m in range(1,self.M+1):
            step_list = []
            for n in range(0,self.M-m+1):
                step_list.append(self.step_value(m,n))
            self.V_tree.append(step_list)   
            #print(self.V_tree[m]) 

        self.print_Value_tree()        

        return

    def print_Value_tree(self):
        #Used to print the entire binomial tree of asset values at each timestep.

        for m in range(0,self.M+1):
            print("Values at timestep {} are:".format(self.M-m))
            for n in range(0,self.M-m+1):
                print("V_{}_{} = {}".format(self.M-m,n,self.V_tree[m][n]))

    def C1_value_tree(self):
        #here we move back to T1 which is the expiry of the underlying call C1 to 
        #understand whether to exercise the option and if so find the current value of C1
        #we require the timestep M' which corresponds to the time T1 and will use the already generated P2 tree to get the needed payoff values
        
        self.M = self.T1 / self.delt #this gets the new Mth timestep
        self.M = int(self.M)
        self.temp_tree = [] #this is needed to ensure we can recycle code from above 

        #this sorts out the payoffs at the top of the C1 tree i.e. at time T1, we can the work backwards
        step_list = [] # loop below sorts out the option values at the final timestep
        for n in range(0,self.M+1):
            payoff = max(self.V_tree[self.M][n] - self.E1, 0)
            step_list.append(payoff)
        self.temp_tree.append(step_list)

        self.V_tree = self.temp_tree #ensures we can still use the regular step method by overwriting the current tree

        #this loop calculates each time step from the final timestep backwards to the current time and the current value of the option
        #Note this runs the opposite way to the asset tree and the upjump counter reflects this
        for m in range(1,self.M+1):
            step_list = []
            for n in range(0,self.M-m+1):
                step_list.append(self.step_value(m,n))
            self.V_tree.append(step_list)   
            #print(self.V_tree[m]) 

        self.print_Value_tree()

        return
    

class Put_on_call(Option):
    #put on call P1 allows holder to buy a call C2 on an underlying asset at time T1 where C2 has expiry T2
    #we deal with the call C2 firstly then work to value P1 from this 
    def __init__(self,asset,E):
        self.type = "Put on call"
        self.E2 = float(E) #strike price of underlying call C2
        self.T2 = asset.T #expiry time of underlying call C2(comes from the asset tree final time)   
        self.M = asset.M #number of timesteps
        self.p = asset.p #probability from the asset class
        self.r = asset.r #interest rate
        self.delt = asset.delt #timestep difference
        self.asset_tree = asset.asset_tree
        self.Am = "N"
        self.T1 = float(input("Enter expiry of the put P1: "))
        self.E1 = float(input("Enter the strike price of put P1: "))

        self.print_option_conditions()
        self.Value_tree_method()
        self.P1_value_tree()

        return

    def print_option_conditions(self):
        print("Option is a Put P1, with expiry {} and strike price {} on an underlying call C2.".format(self.T1,self.E1))
        print("Where C2 has expiry {} and strike price {} on an underlying asset S".format(self.T2,self.E2))

        return


    def payoff(self,m,n): 
        #gets the payoff for the call C2, this will be used at top/max timestep M in the tree for euro call and at each step for american calls
        #print(self.asset_tree[m][n])
        V = max(self.asset_tree[m][n]-self.E2,0)
        return V  

    def step_value(self,m,n):
        #gets value of the option at a given timestep for each number of upjumps within that timestep
        
        correction_factor = math.exp(-self.r*self.delt) #time value of money factor from the asset

        value = correction_factor * (self.p * self.V_tree[m-1][n+1] + (1-self.p) * self.V_tree[m-1][n])       

        if self.Am == "Y":
            payoff = self.payoff(self.M-m,n)
            print(payoff,value)
            return max(payoff,value)
        else:
             return value  

    def Value_tree_method(self):
        
        self.V_tree = [] #list for the option values V at each timestep
        step_list = [] # loop below sorts out the option values at the final timestep
        for n in range(0,self.M+1):
            step_list.append(self.payoff(self.M,n))
        self.V_tree.append(step_list)

        #print(self.V_tree)
        
        #this loop calculates each time step from the final timestep backwards to the current time and the current value of the option
        #Note this runs the opposite way to the asset tree and the upjump counter reflects this
        for m in range(1,self.M+1):
            step_list = []
            for n in range(0,self.M-m+1):
                step_list.append(self.step_value(m,n))
            self.V_tree.append(step_list)   
            #print(self.V_tree[m]) 

        self.print_Value_tree()        

        return

    def print_Value_tree(self):
        #Used to print the entire binomial tree of asset values at each timestep.

        for m in range(0,self.M+1):
            print("Values at timestep {} are:".format(self.M-m))
            for n in range(0,self.M-m+1):
                print("V_{}_{} = {}".format(self.M-m,n,self.V_tree[m][n]))

    def P1_value_tree(self):
        #here we move back to T1 which is the expiry of the put P1 to 
        #understand whether to exercise the option and if so find the current value of P1
        #we require the timestep M' which corresponds to the time T1 and will use the already generated C2 tree to get the needed payoff values
        
        self.M1 = self.T1 / self.delt #this gets the new Mth timestep
        self.M1 = int(self.M1)
        self.temp_tree = [] #this is needed to ensure we can recycle code from above 

        #this sorts out the payoffs at the top of the P1 tree i.e. at time T1, we can the work backwards
        step_list = [] # loop below sorts out the option values at the final timestep
        for n in range(0,self.M1+1):
            payoff = max(self.E1 - self.V_tree[self.M - self.M1][n], 0)
            step_list.append(payoff)
        self.temp_tree.append(step_list)

        self.V_tree = self.temp_tree #ensures we can still use the regular step method by overwriting the current tree

        #this loop calculates each time step from the final timestep backwards to the current time and the current value of the option
        #Note this runs the opposite way to the asset tree and the upjump counter reflects this
        for m in range(1,self.M1+1):
            step_list = []
            for n in range(0,self.M1-m+1):
                step_list.append(self.step_value(m,n))
            self.V_tree.append(step_list)   
            #print(self.V_tree[m]) 
        self.M = self.M1
        self.print_Value_tree()

        return

#TESTS BELOW THIS POINT
share = asset(0.5,2,0.01,1,2,5)

share.asset_tree()

#call_test = Option(share,"Call",2.5)

#put_test = Option(share,"Put",2.5)

#cash_test = Option(share,"C or N",2.5)

#asset_test = Option(share,"A or N",6)

#call_on_call_test = Option(share, "Call on call", 2) #last number is strike price E2 for call C2

#call_on_put_test = Option(share, "Call on put", 2.5) #last number is strike price E2 for put P2

#Note Tree is in reverse order so indicies must be changed to ensure correct level of tree is accessed when valuing compound options 
#Could always use an algorithm to reverse the tree before accessing it which would arguably be better!!!

#put_on_call_test = Option(share, "Put on call", 2.5) #last number is strike price E2 for call C2
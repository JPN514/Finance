#Program to for binomial tree method of option valuation
#VERSION BELOW HAS BEEN CLEANED UP ON 20/10/2022

#We will value the asset S then work backwards through a binary tree to calculate
#the value of an option at time t=0 where S is the underlying asset for the option.
#Will deal with two cases on how to value the underlying asset price with discretised random walks?
#This is because an extra assumption is needed to solve the system that is produced
#We will use 3FIN notes where the continuous random walk is turned to a discrete random walk which is justified in the notes.
#Case values u,d,p calculated by expected values and variance 

#IMPORTANT TO-DOs:
# round consistently throughout!!!
# Tests on all !!!
# sort for underlying asset which pays continuous dividend D_0

import math
import numpy as np
import sympy as sym

class asset(): #class for the underlying asset for which the options seek to buy/sell
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
        self.asset_tree()
        

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



class Call(Option):
#Agreement made to have option to buy an underlying asset at time T
#for strike price E
    def __init__(self,asset,E):
        self.type = "Call"
        self.E = float(E)
        self.T = asset.T #expiry time   
        self.M = asset.M #number of timesteps
        self.p = asset.p #probability from the asset class
        self.r = asset.r #interest rate
        self.delt = asset.delt #timestep difference
        self.asset_tree = asset.S
        #self.create_asset_tree(asset)
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

class Put(Option):
#Option to sell underlying asset for strike price E at expiry time T
    def __init__(self,asset,E):
            self.type = "Put"
            self.E = float(E)
            self.T = asset.T #expiry time   
            self.M = asset.M #number of timesteps
            self.p = asset.p #probability from the asset class
            self.r = asset.r #interest rate
            self.delt = asset.delt #timestep difference
            self.asset_tree = asset.S
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
        self.asset_tree = asset.S
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
        self.asset_tree = asset.S 
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

class Call_on_call(Call):
     #call on call C1 allows holder to buy a call C2 on an underlying asset at time T1 where C2 has expiry T2
    #this is done by passing C2 in as the asset for the call
    #could possibly just pass one call into another but unsure ???

    def __init__(self,C2,E):
        self.type = "Call on call"
        self.T = float(input("Enter expiry of the call C1: "))
        self.E = float(E) #strike price of call C1
        self.M1 = C2.M
        self.T2 = C2.T #expiry time of underlying call C2(comes from the asset tree final time)   
        self.p = C2.p #probability from the asset class
        self.r = C2.r #interest rate
        self.delt = C2.delt #timestep difference
        self.asset_tree = C2.V_tree
        self.Am = "N"
        self.M = int(self.T / self.delt)
        

        self.print_option_conditions()
        #print(self.asset_tree)
        self.asset_tree.reverse() #have to reverse the order of the asset tree(Values of C2 in this case) to access correct indexes
        #print(self.asset_tree)
        self.Value_tree_method()
        

        return

class Call_on_put(Call):
#call on put C1 allows holder to buy a put P2 on an underlying asset at time T1 where P2 has expiry T2
    #this is done by passing P2 in as the asset for the call
    def __init__(self,P2,E):
        self.type = "Call on put"
        self.T = float(input("Enter expiry of the call C1: "))
        self.E = float(E) #strike price of call C1
        self.M1 = P2.M
        self.T2 = P2.T #expiry time of underlying call P2(comes from the asset tree final time)   
        self.p = P2.p #probability from the asset class
        self.r = P2.r #interest rate
        self.delt = P2.delt #timestep difference
        self.asset_tree = P2.V_tree
        self.Am = "N"
        self.M = int(self.T / self.delt)
        

        self.print_option_conditions()
        #print(self.asset_tree)
        self.asset_tree.reverse() #have to reverse the order of the asset tree(Values of C2 in this case) to access correct indexes
        #print(self.asset_tree)
        self.Value_tree_method()
        

        return


class Put_on_call(Put):
    #put on call P1 allows holder to buy a call C2 on an underlying asset at time T1 where C2 has expiry T2
    #this is done by passing C2 in as the asset for the put
    def __init__(self,C2,E):
        self.type = "Put on call"
        self.T = float(input("Enter expiry of the put P1: "))
        self.E = float(E) #strike price of call C1
        self.M1 = C2.M
        self.T2 = C2.T #expiry time of underlying call P2(comes from the asset tree final time)   
        self.p = C2.p #probability from the asset class
        self.r = C2.r #interest rate
        self.delt = C2.delt #timestep difference
        self.asset_tree = C2.V_tree
        self.Am = "N"
        self.M = int(self.T / self.delt)
        

        self.print_option_conditions()
        #print(self.asset_tree)
        self.asset_tree.reverse() #have to reverse the order of the asset tree(Values of C2 in this case) to access correct indexes
        #print(self.asset_tree)
        self.Value_tree_method()
        

        return

class Put_on_put(Put):
    #put on call P1 allows holder to buy a put P2 on an underlying asset at time T1 where P2 has expiry T2
    #this is done by passing P2 in as the asset for the put
    def __init__(self,P2,E):
        self.type = "Put on put"
        self.T = float(input("Enter expiry of the put P1: "))
        self.E = float(E) #strike price of call C1
        self.M1 = P2.M
        self.T2 = P2.T #expiry time of underlying call P2(comes from the asset tree final time)   
        self.p = P2.p #probability from the asset class
        self.r = P2.r #interest rate
        self.delt = P2.delt #timestep difference
        self.asset_tree = P2.V_tree
        self.Am = "N"
        self.M = int(self.T / self.delt)
        

        self.print_option_conditions()
        #print(self.asset_tree)
        self.asset_tree.reverse() #have to reverse the order of the asset tree(Values of C2 in this case) to access correct indexes
        #print(self.asset_tree)
        self.Value_tree_method()
        

        return

#TESTS BELOW THIS POINT::

share = asset(0.5,2,0.01,1,2,5)

#call_test = Call(share,2.5)
#put_test = Put(share,2.5)

#cash_or_nothing_test = Cash_or_nothing(share,2.5,5,"Call")
#asset_or_nothing_test = Asset_or_nothing(share,2.5,"Call")

#call_on_call = Call_on_call(call_test,2.5)
#call_on_put = Call_on_put(put_test,0.5)
#put_on_call = Put_on_call(call_test,1.5)
#put_on_put = Put_on_put(put_test,1)
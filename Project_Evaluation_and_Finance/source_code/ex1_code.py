import numpy as np
import scipy.stats as st
from scipy.optimize import root_scalar as RS

class BlaSchMet:
    def __init__(self, S, K, T, rf, div_y, option_type):
        self.spot = S
        self.strike = K
        self.total_time = T
        self.risk_free = rf
        self.dividend_yield = div_y
        self.option_type = option_type
        self.volatility = None
        self.find_price = None
        self.option_price = None
        self.d1 = None
        self.d2 = None
        self.x =  None

    
    def set_goal(self, find_price=None, vol=None, find_vol=None, price=None):
        
        if find_price==True:
            self.find_price = True
            self.volatility = vol
        elif find_vol == True:
            self.find_vol = True
            self.option_price = price
        else: 
            print('*State desired goal')
    

    def d1_func(self,post=None):
        part1 = np.log(self.spot/self.strike)
        part2 = (self.risk_free-self.dividend_yield+(1/2)*self.volatility**2)*self.total_time
        part3 = self.volatility*np.sqrt(self.total_time)
        d1 =  (part1+part2) / part3
        self.d1 = d1
        if post == True:
            return self.d1


    def d2_func(self, d1, post=None):
        d2 = d1 - self.volatility*np.sqrt(self.total_time)
        self.d2 = d2
        if post==True:
            return self.d2


    def call_black_scholes(self,x=None, *args):
        if self.x != None:
            self.volatility = x
        part1 = self.spot*np.e**(-self.dividend_yield*self.total_time)*st.norm.cdf(self.d1_func(post=True))
        part2 = self.strike * np.e**(-self.risk_free*self.total_time)*st.norm.cdf(self.d2_func(self.d1,post=True))
        call_price = part1-part2
        disc_strike = self.strike*np.e**(-self.risk_free*self.total_time)
        disc_spot = self.spot*np.e**(-self.dividend_yield*self.total_time)
        if self.option_type=='Call':
            price = call_price
            if self.find_price==True:
                return price
            if self.find_vol==True:
                return price-self.option_price
            
        elif self.option_type=='Put':
            price = call_price+disc_strike-disc_spot
            if self.find_price==True:
                return price
            if self.find_vol==True:
                return price-self.option_price
        else:
            print('*State option_type')


    def find_imp_vol(self, x_guess=None):
        self.x = x_guess
        self.volatility = self.x
        result = RS(self.call_black_scholes, args=(self.option_price,), x0=x_guess, bracket=[0.0001, 1])
        return round(result.root,3)
    

    def vega_calc(self):
        part1 = 1/100 
        part2 = self.spot * np.e**(-self.dividend_yield*self.total_time) * np.sqrt(self.total_time)
        part3 = (np.e**((-self.d1_func(post=True)**2)/2))/2
        result = part1 * part2 *part3
        return result
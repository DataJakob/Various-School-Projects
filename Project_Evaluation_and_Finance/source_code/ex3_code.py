import numpy as np 
import matplotlib.pyplot as plt

class BinPriMod:
    def __init__(self, S, K, sigma, total_time, period_timespan, rate_i, rate_dy,
                 option_type, exercise_style):
        self.spot = S
        self.strike = K
        self.risk = sigma
        self.total_time = total_time
        self.period_time_span = period_timespan
        self.risk_free = rate_i
        self.dividend_yield = rate_dy
        self.option_type = option_type
        self.exercise_style = exercise_style
        self.n_periods = int(self.total_time / self.period_time_span)
        self.values = None
        self.prices = None


    def help():
        print('def __init__(self, S, K, sigma, total_time, period_timespan, rate_i, rate_dy,option_type, exercise_style):')
        print('\n')
        print('Attributes:\n    up_and_down,\n  storage_values,\n   option_price')


    def up_and_down(self, spot):   
        uS = spot*np.e**((self.risk_free - self.dividend_yield) * 
                              self.period_time_span + self.risk*np.sqrt(self.period_time_span)) 
        dS = spot*np.e**((self.risk_free -self.dividend_yield) * 
                              self.period_time_span - self.risk*np.sqrt(self.period_time_span))
        return [uS, dS]


    def storage_values(self, post=None):
        storage = [[self.spot]]
        for i in range(0, self.n_periods,1):
            sub_storage = []
            for j in range(0, len(storage[i]),2):   
                sub_storage.append(np.array(self.up_and_down(storage[i][j])))
            if (i+1)>=2:
                if (i+1)%2== 0:
                    sub_storage.append(np.reshape(self.up_and_down(storage[i][j+1])[1],(1,)))                                            
            fixed = np.concatenate(sub_storage)
            storage.append(np.round(fixed,3))
        self.values = storage
        if post == True:
            return self.values 


    def option_price(self, 
                     up, down, alt_spot,
                     high_optpri, low_optpri):
        u = up/alt_spot
        d = down/alt_spot
        p = (np.e**((self.risk_free-self.dividend_yield)*self.period_time_span)-d)/(u-d)

        opt_price = np.e**(-self.risk_free*self.period_time_span)*((high_optpri*p)+(low_optpri*(1-p)))

        if self.exercise_style == 'European':
            opt_price = opt_price
        elif self.exercise_style == 'American':
            if self.option_type =='Put':
                opt_price = max(opt_price, self.strike - alt_spot)
            else:
                opt_price = max(opt_price, alt_spot-self.strike)            
        else:
            print('State exercise style!!!')
        return round(opt_price,3)
    

    def storage_prices(self, post=None):
        latest_opt_pri = []
        if self.option_type=='Call':
            array = np.where(self.values[self.n_periods]-self.strike>0,self.values[self.n_periods]-self.strike,0)
        elif self.option_type=='Put':
            array = np.where(self.values[self.n_periods]-self.strike<0,self.values[self.n_periods]-self.strike,0)
        else:
            print('State option type!!!')
        latest_opt_pri.append(abs(array))
        for i in range(0, self.n_periods, 1): 
            sub_optpri_storage = []
            for j in range(0,self.n_periods-i,1):   #periods- 1
                sub_optpri_storage.append(self.option_price(self.values[self.n_periods][j], 
                                                            self.values[self.n_periods][j+1],
                                                            self.values[self.n_periods-1][j],
                                                            latest_opt_pri[i][j], 
                                                            latest_opt_pri[i][j+1]))
            latest_opt_pri.append(np.round(sub_optpri_storage,2))
        self.prices = np.flip(latest_opt_pri)
        if post == True:
            return self.prices
        return self.prices
    

    def plot_tree(self,txt_shift):
        fig, ax = plt.subplots(figsize=(6,6))
        for i in range(0,int(self.n_periods)+1,1):
            ax.scatter(x=np.repeat((i)*1,i+1), y= self.values[i])
            for j in range(0,i+1,1):
                text_value = 'Value '+ str(self.values[i][j])
                text_price = 'Price '+ str(self.prices[i][j])
                ax.annotate(text_value, xy=(i*1, self.values[i][j]+txt_shift))
                ax.annotate(text_price, xy=(i*1, self.values[i][j]-txt_shift))
            ax.set_xlabel('Periods')
        ax.set_ylabel('Price')
        plt.xlim(-1,self.n_periods+2*self.period_time_span)
        plt.title('Binomial tree for '+self.exercise_style+' '+self.option_type+' option')
        plt.show()
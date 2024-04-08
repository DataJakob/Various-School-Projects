import pandas as pd
import numpy as np
import statsmodels.api as sm

class LeaSquMonCar():
    def __init__(self, S, K, T, vol, rf,  div_y, option_type, paths, time_steps):
    # def __init__(self, S, K, T, vol, rf,  div_y, option_type, paths, time_steps, df):
        self.spot = S
        self.strike = K
        self.total_time = T
        self.volatility = vol
        self.risk_free =  rf
        self.dividend_yield = div_y
        self.paths = paths
        self.time_steps = time_steps
        self.h =  self.total_time/self.time_steps
        self.option_type = option_type
        # self.pathdf =  df
        self.pathdf = None
        self.payoffdf = None

    def CreatePaths(self,post=None):
        path_list = []
        for path in range(self.paths):
            path_i = [self.spot]
            for steps in range(self.time_steps):
                part1 = (self.risk_free-self.dividend_yield*(1/2)*self.volatility**2)*self.h
                part2 = np.random.normal(0,1)
                part3 = self.volatility * np.sqrt(self.h)*part2
                S_t = path_i[-1]*np.e**(part1+part3)
                path_i.append(S_t)
            path_list.append(path_i)
        pathsdf = pd.DataFrame(path_list).T
        self.pathdf = pathsdf
        if post == True:
            return  pathsdf
        
    def regress(self, X, Y):
        Xsq = X**2
        df = pd.DataFrame({'id':np.arange(self.paths),
                        'Y':Y,
                        'X':X,
                        'Xsq':Xsq})
        if self.option_type =='Call':
            df=df[df['X']>self.strike]
        elif self.option_type == 'Put':
            df=df[df['X']<self.strike]
        else:  
            None
            
        train = sm.add_constant(df[['X','Xsq']])
        model = sm.OLS(df['Y'],train).fit()
        cond_exp = list(model.params[0]+model.params[1]*train['X']+model.params[2]*train['Xsq'])
        if self.option_type == 'Call':
            boolean = pd.Series([(cond_exp[i]>(X[i]-self.strike)) for i in range(len(train))])
            b = pd.Series(np.where(boolean==True, df['Y'],0), index=df.index)
            b1 = pd.Series(np.where(boolean==False,1,0), index=df.index)
        if self.option_type == 'Put':
            boolean = pd.Series([cond_exp[i]>(self.strike-X[i]) for i in range(len(train))])
            b = pd.Series(np.where(boolean==True, Y,0), index=df.index)        
            b1 = pd.Series(np.where(boolean==False,1,0), index=df.index)
        return [b,b1]
        
    def LeastSquares(self,post=None):
        iddf = self.pathdf.T
        iddf['id'] = np.arange(self.paths)
        Payoff_df = iddf
        disc_r = np.e**((-self.risk_free+self.dividend_yield)*self.h)


        for i in range(0,self.time_steps-1,1):
            data_retY = iddf[self.time_steps-i]
            data_retX = iddf[self.time_steps-(i+1)]
            
            if self.option_type == 'Call':
                if i==0:
                    Y =np.where(data_retY-self.strike>0,data_retY-self.strike,0)*disc_r
                else:
                    Y = Payoff_df[self.time_steps-i]*disc_r
                X = np.where(data_retX-self.strike>0,data_retX,0)
            ################
            if self.option_type == 'Put':
                if i == 0:
                    Y =np.where(self.strike-data_retY>0,self.strike-data_retY,0)*disc_r
                else:
                    Y = Payoff_df[self.time_steps-i]*disc_r
                X = np.where(self.strike-data_retX>0,data_retX,0)
            ################
            cond_exp  = self.regress(X,Y)
            zeros = pd.Series(np.zeros(self.paths))
            zeros.loc[cond_exp[0].index] =  cond_exp[0]/disc_r
            Payoff_df[self.time_steps-i] = np.where(zeros>Y,zeros,0)
            ###################
            zeros = pd.Series(np.zeros(self.paths))
            zeros.loc[cond_exp[1].index] =  cond_exp[1]
            if self.option_type == 'Call':
                rest = np.where(X-self.strike != self.strike, X-self.strike,0)
            else:
                rest = np.where(self.strike-X != self.strike, self.strike-X,0)
            Payoff_df[self.time_steps-(i+1)] = np.where(zeros==1,rest,0)
        ###############################
        for idx in range(Payoff_df.shape[0]):
            row = Payoff_df.iloc[idx,1:]
            reset = 0
            for val in range(1,Payoff_df.shape[1]-1):
                if reset == 0:
                    
                    if row[val] > 0:
                        reset += 1
                else:
                    row[val] = 0
            Payoff_df.iloc[idx,1:] = row
        self.payoffdf = Payoff_df
        if post==True:
            return Payoff_df
    
    def PlotEarlyExercise(self):
        # fig, ax = plt.subplots()
        xes = []
        yes = []
        for i in range(0,len(self.payoffdf),1):
            x = np.where(self.payoffdf.iloc[i,1:-1]>0)
            y = sum(self.payoffdf.iloc[i,1:-1])
            if len(x[0]) != 0:
                # if self.option_type == 'Call':
                    # ax.scatter(x[0][0]+1, self.strike+y, color='red', alpha=.3)
                # else:
                    # ax.scatter(x[0][0]+1, self.strike-y, color='red', alpha=.3)
                # ax.plot(self.pathdf[i],color='grey',alpha=0.3)
                xes.append(x[0][0])
                yes.append(y)
        return [xes,yes]
        

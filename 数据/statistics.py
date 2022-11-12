import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from datetime import datetime 
import math
from scipy.stats import mstats

def quick_sort(data):
    """quick_sort"""
    if len(data) >= 2:
        mid = data[len(data)//2]
        left,right = [], []
        data.remove(mid)
        for num in data:
            if num >= mid:
                right.append(num)
            else:
                left.append(num)
        return quick_sort(left) + [mid] + quick_sort(right)
    else:
        return data

class goods():
	def __init__(self,price,trade_fee):
		self.price=price
		self.trade_fee=trade_fee
		
		self.max_reduce=0
		self.max_increase=0
		self.rate_of_change=[]
		self.rate_of_change_sorted=[]
		self.increase_weight=0
		self.reduce_weight=0
	
	'''
	获取该标的增长率
	'''
	def get_rate_of_change(self):
		rate_of_change=[]
		rate_of_change.append(0.0)
		for i in range(1,len(self.price)):
			rate=(self.price[i]-self.price[i-1])/self.price[i]
			rate_of_change.insert(i,rate)
		return rate_of_change
	
	'''
	得到标的物极限涨跌的界限
	'''
	def get_percentage_number(self,percentage):
		a=quick_sort(self.rate_of_change)
		limit=math.floor(percentage*len(a))
		number=a[limit]
		return number
		'''
	统计大幅上涨或下跌后的升降次数，算出概率
	如果出现在周五，后一天的增长率必维0，那就去后面收个不为0的来计算
	'''
	'''
	up taolun
	'''
	def increase_rate_stats(self):
		'''change to dict'''
		num=0
		revenue_increase=0
		revenue_reduce=0
		for i in range(len(self.rate_of_change)):
			if self.rate_of_change[i]>self.max_increase:
				if self.rate_of_change[i+1]>0:
					revenue_increase+=self.rate_of_change[i+1]/self.rate_of_change[i]
				if self.rate_of_change[i+1]<0:
					revenue_reduce+=self.rate_of_change[i+1]/self.rate_of_change[i]
				if self.rate_of_change[i+1]==0:
					j=i+2
					if self.rate_of_change[j]==0:
						j+=1
						continue
					if self.rate_of_change[j]>0:
						revenue_increase+=self.rate_of_change[i+1]/self.rate_of_change[i]
					if self.rate_of_change[j]<0:
						revenue_reduce+=self.rate_of_change[i+1]/self.rate_of_change[i]
						'''
						jianhua function
						'''
				num+=1
		increase_weight=(revenue_increase+revenue_reduce)/num
		
		return increase_weight

	'''
	down taolun
	'''
	def reduce_rate_stats(self):
		'''change to dict'''
		num=0
		revenue_increase=0
		revenue_reduce=0
		for i in range(len(self.rate_of_change)):
			if self.rate_of_change[i]<self.max_reduce:
				if self.rate_of_change[i+1]>0:
					revenue_increase+=self.rate_of_change[i+1]/self.rate_of_change[i]
				if self.rate_of_change[i+1]<0:
					revenue_reduce+=self.rate_of_change[i+1]/self.rate_of_change[i]
				if self.rate_of_change[i+1]==0:
					j=i+2
					if self.rate_of_change[j]==0:
						j+=1
						continue
					if self.rate_of_change[j]>0:
						revenue_increase+=self.rate_of_change[i+1]/self.rate_of_change[i]

					if self.rate_of_change[j]<0:
						revenue_reduce+=self.rate_of_change[i+1]/self.rate_of_change[i]
				num+=1

		reduce_weight=(revenue_increase+revenue_reduce)/num

		return reduce_weight

def get_average_5days_price(price,i):
	if i>=4:
		average_5days_price=(price[i]+price[i-1]+price[i-2]+price[i-3]+price[i-4])/5
		return average_5days_price
	else:
		sum_price=0
		count=0
		while i!=-1:
			sum_price+=price[i]
			i-=1
			count+=1
		average_5days_price=sum_price/count
		return average_5days_price


df_gold = pd.read_csv(r'C:\Users\zz156\Desktop\2022_Problem_C_DATA\LBMA-GOLD.csv')
df_bitcoin = pd.read_csv(r'C:\Users\zz156\Desktop\2022_Problem_C_DATA\BCHAIN-MKPRU.csv')	

'''
处理黄金里的空值，使其与前一天等价，增长率为0，不影响选择，后期增长率直接为之后的可能增长率
'''
for i in range(len(df_gold['USD (PM)'])):
	if df_gold['USD (PM)'].isnull()[i]==True:
		df_gold['USD (PM)'][i]=df_gold['USD (PM)'][i-1]

'''
变换为list方便后续补充插值
'''
usd_pm=df_gold['USD (PM)'].tolist()
date_gold=df_gold['Date'].tolist()

date_bitcoin=df_bitcoin['Date'].tolist()
value=df_bitcoin['Value'].tolist()

trade_fee_gold=0.01
trade_fee_bitcoin=0.02

weekend=[]

'''
处理不规则的时间
'''
for i in range(len(date_gold)):
	a=date_gold[i].split('/')
	b=a[0]
	c=a[1]
	d=a[2]
	if int(b)>2000:
		b=b%2000
		e=str(b+'/'+c+'/'+d)
		date_gold[i].replace(e)
		
for i in range(len(date_bitcoin)):
	a=date_bitcoin[i].split('/')
	b=a[0]
	c=a[1]
	d=a[2]
	if int(b)>2000:
		b=b%2000
		e=str(b+'/'+c+'/'+d)
		date_bitcoin[i].replace(e)
'''
补充闭市时间，保证序列长度一致，添加闭市时间，以便下一步区分
'''

for i in range(len(usd_pm)):
	if usd_pm[i]=='None':
		usd_pm[i]=usd[i-1]
		
		
for i in range(len(date_bitcoin)):
	if date_bitcoin[i] not in date_gold:
		date_gold.insert(i,date_bitcoin[i])
		usd_pm.insert(i,usd_pm[i-1])
		weekend.append(date_bitcoin[i])

'''
基础信息存储
'''
gold=goods(usd_pm,trade_fee_gold)
gold.rate_of_change=gold.get_rate_of_change()
gold.rate_of_change_sorted=quick_sort(gold.get_rate_of_change())
gold.max_reduce=gold.get_percentage_number(0.02)
gold.max_increase=gold.get_percentage_number(0.98)
gold.increase_weight=gold.increase_rate_stats()
gold.reduce_weight=gold.reduce_rate_stats()


bitcoin=goods(value,trade_fee_bitcoin)
bitcoin.rate_of_change=bitcoin.get_rate_of_change()
bitcoin.rate_of_change_sorted=quick_sort(bitcoin.get_rate_of_change())
bitcoin.max_reduce=bitcoin.get_percentage_number(0.02)
bitcoin.max_increase=bitcoin.get_percentage_number(0.98)
bitcoin.increase_weight=bitcoin.increase_rate_stats()
bitcoin.reduce_weight=bitcoin.reduce_rate_stats()

portfolio=[1000,0,0]
summa=usd_pm[0]*(1+trade_fee_gold)+value[0]*(1+trade_fee_bitcoin)
rate=portfolio[0]/summa
portfolio[1]=rate
portfolio[2]=rate
portfolio[0]=0
portfolio_price=[]
portfolio_price.append(math.log(rate*(usd_pm[0]+value[0])))

for i in range(1,len(gold.rate_of_change)):
	usd_pm_in=usd_pm[i]*(1+trade_fee_gold)
	value_in=value[i]*(1+trade_fee_bitcoin)
	value_out=value[i]*(1-trade_fee_bitcoin)
	usd_pm_out=usd_pm[i]*(1-trade_fee_gold)
	gold_5=get_average_5days_price(gold.price,i)
	bitcoin_5=get_average_5days_price(bitcoin.price,i)
	
	
	change_fee=1-(1-gold.trade_fee)*(1-bitcoin.trade_fee)
	revenue_exp_bitcoin=0
	revenue_exp_gold=0
	
	if date_gold[i] not in weekend:
		if gold.rate_of_change[i]>gold.max_increase or gold.rate_of_change[i]<gold.max_reduce or bitcoin.rate_of_change[i]>bitcoin.max_increase or bitcoin.rate_of_change[i]<bitcoin.max_reduce:
			if gold.rate_of_change[i]>gold.max_increase:
				revenue_exp_gold=gold.price[i]*gold.increase_weight
			if gold.rate_of_change[i]<gold.max_reduce:
				revenue_exp_gold=gold.price[i]*gold.reduce_weight
			if bitcoin.rate_of_change[i]>bitcoin.max_increase:
				revenue_exp_bitcoin=bitcoin.price[i]*bitcoin.increase_weight
			if bitcoin.rate_of_change[i]<bitcoin.max_reduce:
				revenue_exp_bitcoin=bitcoin.price[i]*bitcoin.reduce_weight
	
			if revenue_exp_gold<=-change_fee and revenue_exp_bitcoin<=-change_fee:
				portfolio[0]+=portfolio[1]*usd_pm_out+portfolio[2]*value_out
				portfolio[1]=0
				portfolio[2]=0
			
			if revenue_exp_gold<=-change_fee and revenue_exp_bitcoin>-change_fee and revenue_exp_bitcoin<=bitcoin.trade_fee:
				portfolio[0]+=portfolio[1]*usd_pm_out
				portfolio[1]=0
				
			if revenue_exp_gold>change_fee and revenue_exp_bitcoin<change_fee:
				portfolio[1]+=portfolio[0]/usd_pm_in+portfolio[2]*value_out/usd_pm_in
				portfolio[0]=0
				portfolio[2]=0
		
			if revenue_exp_gold<change_fee and revenue_exp_bitcoin>change_fee:
				portfolio[2]+=portfolio[0]/value_in+portfolio[1]*usd_pm_out/value_in
				portfolio[1]=0
				portfolio[0]=0
			
			
			
			if revenue_exp_gold>gold.trade_fee and revenue_exp_bitcoin>bitcoin.trade_fee and portfolio[0]!=0:
				summa=usd_pm[i]*(1+trade_fee_gold)+value[i]*(1+trade_fee_bitcoin)
				rate=portfolio[0]/summa
				portfolio[1]+=rate
				portfolio[2]+=rate
				portfolio[0]=0
			if revenue_exp_gold>gold.trade_fee and revenue_exp_bitcoin<bitcoin.trade_fee and portfolio[0]!=0:
				summa=usd_pm[i]*(1+trade_fee_gold)
				rate=portfolio[0]/summa
				portfolio[1]+=rate
				portfolio[2]+=rate
				portfolio[0]=0
			if revenue_exp_gold<gold.trade_fee and revenue_exp_bitcoin>bitcoin.trade_fee and portfolio[0]!=0:
				summa=value[i]*(1+trade_fee_bitcoin)
				rate=portfolio[0]/summa
				portfolio[1]+=rate
				portfolio[2]+=rate
				portfolio[0]=0
		else:
			if gold.price[i]>gold_5*(1+change_fee) and bitcoin.price[i]<bitcoin_5*(1+change_fee):
				portfolio[1]+=portfolio[0]/usd_pm_in+portfolio[2]*value_out/usd_pm_in
				portfolio[0]=0
				portfolio[2]=0
			if gold.price[i]<gold_5*(1+change_fee) and bitcoin.price[i]>bitcoin_5*(1+change_fee):
				portfolio[2]+=portfolio[0]/value_in+portfolio[1]*usd_pm_out/value_in
				portfolio[1]=0
				portfolio[0]=0
			if gold.price[i]>gold_5*(1+gold.trade_fee) and gold.price[i]<gold_5*(1+change_fee) and bitcoin.price[i]<bitcoin_5*(1+gold.trade_fee):
				portfolio[0]+=portfolio[1]*usd_pm_out
				portfolio[1]=0
				
			if gold.price[i]>gold_5 and bitcoin.price[i]>bitcoin_5:
				summa=usd_pm[i]*(1+trade_fee_gold)+value[i]*(1+trade_fee_bitcoin)
				rate=portfolio[0]/summa
				portfolio[1]+=rate
				portfolio[2]+=rate
				portfolio[0]=0
	a=math.log(portfolio[0]+portfolio[1]*gold.price[i]+portfolio[2]*bitcoin.price[i])
	portfolio_price.append(a)

for i in range(len(usd_pm)):
	usd_pm[i]=math.log(usd_pm[i])
	
for i in range(len(value)):
	value[i]=math.log(value[i])



ax=plt.subplot(2,1,1)
plt.plot(date_gold,usd_pm,color='red',label='gold')
plt.plot(date_bitcoin,value,color='blue',label='bitcoin')
plt.plot(date_gold,portfolio_price,color='green',label='portfolio')

plt.xlabel('Date')
plt.ylabel('Price(logarith)')
tick_spacing = 180
ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
plt.legend(loc='upper left')
plt.show()	





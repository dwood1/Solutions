import numpy as np
import matplotlib.pyplot as plt
from binance.client import Client
import time
#from keras.layers import LSTM, Dense, TimeDistributed, Dropout
#from keras.models import Sequential
#from keras import optimizers
from sklearn.preprocessing import MinMaxScaler
import sys
sys.path.insert(0, 'C:\\Users\\dwood\\Python')
from TemporalFeatures import Features as tp

#-----------------------------------------------------------------------------#

np.random.seed(seed=7)

api_key = 'EdZbJVPs0BmKaDQWr4lw0EXT6deDKcubL9W7Mc66xDLXa2xC78t09PpfLeYY0d4x'
api_secret = 'BG6UffLixG83BdmqwObfuzAVSlhCQBqFBAMFIOQHIphkmBS2CT2qAQcYWFCvy22S'
client = Client(api_key, api_secret)

token = 'ETH'
asset = 'USDT'
duration = 12   #Hours
data_days = 30  #Days

#-----------------------------------------------------------------------------#
pretime = time.time()
klines = client.get_historical_klines(token+asset, Client.KLINE_INTERVAL_1MINUTE,
                                      str(time.time()-(86400*data_days)))

open_price = list([float(i[1]) for i in klines])

print(str(time.time() - pretime))

high_price = list([float(i[2]) for i in klines])
low_price = list([float(i[3]) for i in klines])
close_price = list([float(i[4]) for i in klines])
volume = list([float(i[5]) for i in klines])
quote_asset_volume = list([float(i[7]) for i in klines])
number_of_trades = list([float(i[8]) for i in klines])
taker_buy_base_asset_volume =  list([float(i[9]) for i in klines])
taker_buy_quote_asset_volume = list([float(i[10]) for i in klines])
open_time = list([float(i[0]) for i in klines])
close_time = list([float(i[6]) for i in klines])

#-----------------------------------------------------------------------------#
# Insert the actual bot here
funds_real = client.get_asset_balance(asset=asset)
funds = float(list(funds_real.values())[1])
funds_list = [funds]

tokens_real = client.get_asset_balance(asset=token)    
tokens = float(list(tokens_real.values())[1])
tokens_list = [tokens]  

buy_val_list = [tokens]
sell_val_list = [funds]

buy_price_list = [open_price[-1]]

buybool = False

count=0
while(count < duration*60):
    try:
        time.sleep(55)
        
        funds_real = client.get_asset_balance(asset=asset)
        #        print("Diff between expected and actual funds: "+str(float(list(funds_real.values())[1])-funds))
        funds = float(list(funds_real.values())[1])
        
        tokens_real = client.get_asset_balance(asset=token)    
        #        print("Diff between expected and actual tokens: "+str(float(list(tokens_real.values())[1])-tokens))
        tokens = float(list(tokens_real.values())[1])        
        
        res_01 = tp.resistance(open_price, 315)
        sup_01 = tp.support(open_price, 315)
        res_trend = tp.resistance_trendline(open_price, 2880, 0.6)
        sup_trend = tp.support_trendline(open_price, 2880, 0.6)
        mov_dx = tp.derivative_ratio(open_price, 10)
        
        current_price = float(client.get_symbol_ticker(symbol=token+asset)['price'])
        open_price.append(current_price)
        
        if(((current_price > res_trend[-1] and (current_price > res_01[-1])) 
#                or (mov_dx_01[-1] < 1 - (40/10000))            
                ) and         
                (int(funds) > 10)): 
            buybool = True       
            client.order_market_buy(symbol=token+asset, quantity=int(10*funds/current_price)/10) 
            tokens = tokens + (1-0.001)*(int(10*funds/current_price)/10)
            buy_val_list.append(tokens)
            buy_price_list.append(current_price)
            print("Epoch: " + 
                  str(count) +
                  ", Buy Made @ price: " + 
                  str(current_price) +
                  ", Quantity Bought: " + 
                  str(int(10*funds/current_price)/10) +
                  ", Gain: " +
                  str(buy_val_list[-1]/buy_val_list[-2]))
            funds = funds - current_price*(int(10*funds/current_price)/10)        
        elif((((current_price < sup_01[-1]) and (current_price < sup_trend[-1]))
                or (mov_dx[-1] >= 1 + (120/10000))
                ) and 
                (int(tokens*10)/10 > 10)):   
            buybool = False
            client.order_market_sell(symbol=token+asset, quantity=int(tokens*10)/10)
            funds = funds + (1-0.001)*current_price*int(10*tokens)/10
            sell_val_list.append((1-0.001)*current_price*int(10*tokens)/10)
            print("Epoch: " + 
                  str(count) +
                  ", Sell Made @ price: " +
                  str(current_price) +
                  ", Quantity Sold: " +
                  str(int(tokens*10)/10) +
                  ", Gain: " +
                  str(sell_val_list[-1]/sell_val_list[-2]))
            tokens = tokens - int(tokens*10)/10       
        else:
            funds_list.append(funds)
            tokens_list.append(tokens)  
            print("Epoch: " 
              + str(count) 
              + ", "+token+": " 
              + str(tokens) 
              + ", "+asset+": " 
              + str(funds) 
              + ", Current Price: " 
              + str(current_price) 
              + ", Price Growth:"
              + str(current_price/open_price[-2])
              + ", Asset Growth: " 
              + str(funds/float(funds_list[0])))
        count+=1
    except Exception as e:
        print(e)
        print(str(buybool) + 
        str(int(tokens*10)/10) +
        str(int(funds*1000)/1000))
        time.sleep(59)
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
# Insert the test bot here
li = []

token = 'ETH'
asset = 'USDT'
duration = 12   #Hours
data_days = 30  #Days

#-----------------------------------------------------------------------------#
pretime = time.time()
klines = client.get_historical_klines(token+asset, Client.KLINE_INTERVAL_1MINUTE,
                                      str(time.time()-(86400*data_days)))

open_price = list([float(i[1]) for i in klines])

print(str(time.time() - pretime))

for j in range(1, 2):
    timeNOW = time.time()
    
    res_01 = tp.resistance(open_price, 360)
    sup_01 = tp.support(open_price, 360)
#   
    mov_dx_1 = tp.difference_ratio(open_price, 2)
#    mov_dx_2 = tp.derivative_ratio(open_price, 100)
    
#    movement = tp.movement_ratio(open_price)
    
#    mov_avg_01 = tp.moving_average(open_price, 8*1440)
#    mov_tdssd = tp.moving_tdssd(open_price, 7200)
#    ssd = tp.sample_standard_deviation(open_price)
    
    res_trend = tp.resistance_trendline(open_price, 1440, 0.6)
    sup_trend = tp.support_trendline(open_price, 1440, 0.6)
    print(str(time.time() - timeNOW))
    
    return_sweep = []
    exchange_sweep = []  
    
    for i in range(0, 1, 1):
#        mov_avg = tp.moving_average(open_price, 1440*2)        
        exchange_fee = 0.001
        risk_coeff = 90/100
        
        funds = 10000
        funds_list = [funds]
        tokens = 0
        tokens_list = [(funds+tokens*open_price[0])] 
        value_list = [funds]
        
        exchange_info = []
        
        buy_val = 0
        sell_val = 0
        buy_price = -1                
        for x in range(1, len(open_price)):
            current_price = open_price[x]
            
            fund_check = int(funds*risk_coeff*1000)/1000
            token_sell = int(tokens*risk_coeff*1000)/1000
            
            token_buy = int((funds/current_price)*risk_coeff*1000)/1000
            value_check = int(risk_coeff*current_price*tokens*1000)/1000
            
#            elif((((current_price < sup_01[x]) and (current_price < sup_trend[x])
##                    and (sup_trend[x-1] >= sup_trend[x])
#                    )
#                    or (mov_dx_1[x] >= 1 + (i/10000))
##                    or (mov_dx_2[x] >= 1 + (i/10000))
##                    or (current_price >= buy_price*(1 + 330/10000))
#                    ) and 
#                    (value_check > 10)):   
#                buybool = False                
#                funds = funds + (1-exchange_fee)*current_price*token_sell                
#                tokens = tokens - risk_coeff*tokens
#                exchange_info.append(("Sell", current_price, (1-exchange_fee)*token_sell))
            if(((current_price > res_trend[x] and (current_price > res_01[x])
#                    and (mov_avg_01[x-1] < mov_avg_01[x])
                    )  
                    ) and         
                    (fund_check > 10)): 
                buybool = True                       
                tokens = tokens + (1-exchange_fee)*token_buy                
                funds = funds - current_price*token_buy     
                exchange_info.append(("Buy", current_price, (1-exchange_fee)*token_buy)) 
#                buy_price = current_price
            elif((((current_price < sup_01[x]) and (current_price < sup_trend[x])
#                    and (sup_trend[x-1] >= sup_trend[x])
                )
                or (mov_dx_1[x] >= 0.99 + (0/1000))
#                    or (mov_dx_2[x] >= 1 + (i/10000))
#                    or (current_price >= buy_price*(1 + 330/10000))
                ) and 
                (value_check > 10)):   
                buybool = False                
                funds = funds + (1-exchange_fee)*current_price*token_sell                
                tokens = tokens - risk_coeff*tokens
                exchange_info.append(("Sell", current_price, (1-exchange_fee)*token_sell))
            else:
                funds_list.append(funds)
                tokens_list.append(tokens)         
            
            value_list.append(funds+tokens*current_price) 
        buy_price = -1
        sell_price = -1
        good_trade_count = 1
        bad_trade_count = 1
        buy_is_after_sell = False
        sale_weight = 0
        buy_weight = 0
        for x in exchange_info:
            if x[0] == "Buy":
                if buy_is_after_sell:
                    buy_price = ((buy_price*buy_weight)+(x[1]*x[2]))/(buy_weight+x[2])
                    buy_weight = buy_weight+x[2] 
                else:
                    buy_price = x[1]
                    buy_weight = x[2]
                buy_is_after_sell = True
                sale_weight = 0
            else:
                if not buy_is_after_sell:                    
                    sell_price = ((sell_price*sale_weight)+(x[1]*x[2]))/(sale_weight+x[2])  
                    sale_weight = sale_weight+x[2]                   
                else:
                    sell_price = x[1]
                    sale_weight = x[2]
                buy_is_after_sell = False
                buy_weight = 0
            if buy_price < sell_price and buy_price > 0:
                good_trade_count+=1;
            if sell_price < buy_price and sell_price > 0 and buy_is_after_sell == False:
                bad_trade_count+=1;
#            print("good: "+str(good_trade_count)+"; bad: "+str(bad_trade_count)+"; ")
        print(str(i) +
              ": Return = : " + 
              str(value_list[-1]/value_list[0]) +
              ", Funds: " +     
              str(int(funds*100 )/100) + 
              ", Tokens: " + 
              str(int(tokens*100)/100) +
              ", Trade Ratio: " +
              str(good_trade_count/(good_trade_count + bad_trade_count)) +
              ", Exg. per day: " +
              str((good_trade_count + bad_trade_count)/data_days))        
        return_sweep.append(value_list[-1]/value_list[0])  
        exchange_sweep.append(good_trade_count/(good_trade_count+bad_trade_count)) 
       
#-----------------------------------------------------------------------------#


# Normalize Data
normalize_average = tp.normalize(mov_avg_01)
normalized_value_list = tp.normalize(value_list)
normalized_open_price = tp.normalize(open_price)
normalized_x = tp.normalize(mov_tdssd)
#-----------------------------------------------------------------------------#
# Plotting and Visualization 
plt.plot(normalized_open_price, color='orange')
plt.plot(normalized_value_list, color='black')       
plt.plot(return_sweep)
plt.plot(exchange_sweep)
plt.plot(mov_dx_1)
plt.plot(mov_dx_2)
plt.plot(normalize_average, color='cyan')
plt.plot(open_price)
plt.plot(movement)
plt.hist(movement, bins = 10)    
plt.plot(mov_tdssd)
plt.plot(normalized_x)
lin_reg_forecast = tp.linear_regression_forecast(open_price, 2*1440, 1)
plt.plot(lin_reg_forecast)
#-----------------------------------------------------------------------------#
    # Statistical Model
        # Feature Generation
pred_int = 1440 

#Time Series Features
max_interval = 420    
A = [[x] for x in open_price[:-pred_int]]
length = len(A)
for i in range(15, max_interval+1, 30):     
    train_mov_avg_01 = moving_average(open_price[:-pred_int], i)
    A = [A[t] + [train_mov_avg_01[t]] for t in range(length)]
    
    train_res_01 = get_resistance(open_price[:-pred_int], i)
    A = [A[t] + [train_res_01[t]] for t in range(length)]
    
    train_sup_01 = get_support(open_price[:-pred_int], i)
    A = [A[t] + [train_sup_01[t]] for t in range(length)]
    
    train_res_trend_01 = resistance_trendline(open_price[:-pred_int], i, 0.3)
    A = [A[t] + [train_res_trend_01[t]] for t in range(length)]
    
    train_sup_trend_01 = support_trendline(open_price[:-pred_int], i, 0.3)
    A = [A[t] + [train_sup_trend_01[t]] for t in range(length)]
    
    train_dev_01 = moving_deviation(open_price[:-pred_int], i)
    A = [A[t] + [train_dev_01[t]] for t in range(length)]
    
    train_dx_01 = moving_dx(train_mov_avg_01, 1)
    A = [A[t] + [train_dx_01[t]] for t in range(length)]
    
    train_dx2_01 = moving_dx(train_dx_01, 1)
    A = [A[t] + [train_dx2_01[t]] for t in range(length)]
    
    train_dx3_01 = moving_dx(train_dx2_01, 1)
    A = [A[t] + [train_dx3_01[t]] for t in range(length)]
    
# Simple Time Series Shift
A = [list(reversed(open_price[x-pred_int:x])) for x in range(pred_int, len(open_price))]
    
# Market Features

#-----------------------------------------------------------------------------#
    # Model Preprocessing
    
#Data Processing:
#x = A[max_interval:]
x = A
                       
y = np.array(open_price[pred_int:], ndmin=2)
y = y.reshape((-1, 1))
y = y[max_interval:]

scaler = MinMaxScaler(feature_range = (0,1))
x = scaler.fit_transform(x)
y = scaler.fit_transform(y)

x_train = x[0:round(len(x)*0.7)]
x_test = x[round(len(x)*0.7):len(x)]

y_train = y[0:round(len(y)*0.7)]
y_test = y[round(len(y)*0.7):len(y)]

x_train = np.reshape(x_train, (x_train.shape[0], 1, x_train.shape[1]))
x_test = np.reshape(x_test, (x_test.shape[0], 1, x_test.shape[1]))

y_test = np.reshape(y_test, (y_test.shape[0], 1, y_test.shape[1]))
y_train = np.reshape(y_train, (y_train.shape[0], 1, y_train.shape[1]))

y_test = y_test.reshape((-1, 1))
y_train = y_train.reshape((-1, 1))

#-----------------------------------------------------------------------------#
    # Model Training
    
#Model:
batchSize = 1 #len(x_test)
density_factor = 1
#
model = Sequential()
model.add(LSTM(100, return_sequences = True, activation = 'elu', recurrent_activation = 'elu', unit_forget_bias=True, input_shape=(np.shape(x_train)[1], np.shape(x_train)[2])))
model.add(LSTM(100, return_sequences = True, activation = 'elu', recurrent_activation = 'elu', unit_forget_bias=True))
model.add(LSTM(100, return_sequences = False, activation = 'elu', recurrent_activation = 'elu', unit_forget_bias=True))
model.add(Dense(1, activation = 'relu'))

#model = Sequential()
#model.add(Dense(np.shape(x_train)[1]*density_factor, activation = 'elu', input_shape=(np.shape(x_train)[1],)))
#model.add(Dropout(0.1))
#model.add(Dense(np.shape(x_train)[1]*density_factor, activation = 'elu'))
#model.add(Dropout(0.1))
#model.add(Dense(np.shape(x_train)[1]*density_factor, activation = 'elu'))
#model.add(Dropout(0.1))
#model.add(Dense(np.shape(x_train)[1]*density_factor, activation = 'elu'))
#model.add(Dropout(0.1))
#model.add(Dense(np.shape(x_train)[1]*density_factor, activation = 'elu'))
#model.add(Dense(1, activation = 'relu'))
ADAM = optimizers.adam(lr = 0.0001)
model.compile(loss='mse', optimizer=ADAM) 
model.fit(x_train, y_train, epochs=100, batch_size=(batchSize), verbose=2, shuffle = False)


y_pred = model.predict(x_test)
plt.plot(y_test, color='black')
plt.plot(y_pred, color='cyan')

y_pred_train = model.predict(x_train)
plt.plot(y_train, color='orange')
plt.plot(y_pred_train, color='cyan')

pred_diff = [y_test[x] - y_pred[x] for x in range(len(y_test))]
plt.plot(pred_diff)

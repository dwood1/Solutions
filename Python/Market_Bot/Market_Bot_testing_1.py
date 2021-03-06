import numpy as np
import matplotlib.pyplot as plt
from binance.client import Client
import time
from sklearn.preprocessing import MinMaxScaler
import json
import boto3
import sys
if('C:\\Users\\dwood\\Python' not in sys.path):
    sys.path.insert(0, 'C:\\Users\\dwood\\Python')
from TemporalFeatures import Features as tp


#-----------------------------------------------------------------------------#

np.random.seed(seed=7)

api_key = ''
api_secret = ''
client = Client(api_key, api_secret)

token = 'BTC'
asset = 'USDT'
duration = 12   #Hours
data_days = 1  #Days

#-----------------------------------------------------------------------------#
pretime = time.time()
klines = client.get_historical_klines(token+asset, Client.KLINE_INTERVAL_1MINUTE,
                                      str(time.time()-(86400*data_days)))



print(str(time.time() - pretime))

open_time = list([float(i[0]) for i in klines])
open_price = list([float(i[1]) for i in klines])
high_price = list([float(i[2]) for i in klines])
low_price = list([float(i[3]) for i in klines])
close_price = list([float(i[4]) for i in klines])
volume = list([float(i[5]) for i in klines])
close_time = list([float(i[6]) for i in klines])
quote_asset_volume = list([float(i[7]) for i in klines])
number_of_trades = list([float(i[8]) for i in klines])
taker_buy_base_asset_volume =  list([float(i[9]) for i in klines])
taker_buy_quote_asset_volume = list([float(i[10]) for i in klines])

ACCESS_KEY = ''
SECRET_KEY = ''
SESSION_TOKEN = ''

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name='us-east-1'
)
     
table = dynamodb.Table('Market_Data')

for i in klines:
    table.put_item(
       Item={
            'open_time': i[0],
            'open_price': i[1],
            'high_price': i[2],
            'low_price': i[3],
            'close_price': i[4],    
            'volume': i[5],
            'close_time': i[6],
            'quote_asset_volume': i[7],
            'number_of_trades': i[8],
            'taker_buy_base_asset_volume': i[9],
            'taker_buy_quote_asset_volume': i[10]
        }
    )    

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

flag = True
while(flag):
    try:
        time.sleep(55)
        
        funds_real = client.get_asset_balance(asset=asset)

        funds = float(list(funds_real.values())[1])
        
        tokens_real = client.get_asset_balance(asset=token)    

        tokens = float(list(tokens_real.values())[1])        
        
        res_01 = tp.resistance(open_price, 315)
        sup_01 = tp.support(open_price, 315)
        res_trend = tp.resistance_trendline(open_price, 2880, 0.6)
        sup_trend = tp.support_trendline(open_price, 2880, 0.6)
        mov_dx = tp.derivative_ratio(open_price, 10)
        
        current_price = float(client.get_symbol_ticker(symbol=token+asset)['price'])
        open_price.append(current_price)
        
        # BUY
        if(((current_price > res_trend[-1] and (current_price > res_01[-1])) 
#                or (mov_dx_01[-1] < 1 - (40/10000))            
                ) and         
                (int(funds) > 10)): 
            buybool = True       
            
            #client.order_market_buy(symbol=token+asset, quantity=int(10*funds/current_price)/10) 
            
            order = client.create_test_order(symbol=token+asset,
                                             side=Client.SIDE_BUY,
                                             type=Client.ORDER_TYPE_MARKET,
                                             quantity=int(10*funds/current_price)/10) 
            
            tokens = tokens + (1-0.001)*(int(10*funds/current_price)/10)
            
            buy_val_list.append(tokens)
            
            buy_price_list.append(current_price)
            
            # print("Epoch: " + 
            #       str(count) +
            #       ", Buy Made @ price: " + 
            #       str(current_price) +
            #       ", Quantity Bought: " + 
            #       str(int(10*funds/current_price)/10) +
            #       ", Gain: " +
            #       str(buy_val_list[-1]/buy_val_list[-2]))
            
            funds = funds - current_price*(int(10*funds/current_price)/10
        elif((((current_price < sup_01[-1]) and (current_price < sup_trend[-1]))
                or (mov_dx[-1] >= 1 + (120/10000))
                ) and 
                (int(tokens*10)/10 > 10)):   
            buybool = False
            
            #client.order_market_sell(symbol=token+asset, quantity=int(tokens*10)/10)
            
            order = client.create_test_order(symbol=token+asset,
                                             side=Client.SIDE_SELL,
                                             type=Client.ORDER_TYPE_MARKET,
                                             quantity=int(tokens*10)/10)
            
            funds = funds + (1-0.001)*current_price*int(10*tokens)/10
            
            sell_val_list.append((1-0.001)*current_price*int(10*tokens)/10)
            
            # print("Epoch: " + 
            #       str(count) +
            #       ", Sell Made @ price: " +
            #       str(current_price) +
            #       ", Quantity Sold: " +
            #       str(int(tokens*10)/10) +
            #       ", Gain: " +
            #       str(sell_val_list[-1]/sell_val_list[-2]))
            
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

token = 'BTC'
asset = 'USDT'
duration = 12   #Hours
data_days = 200  #Days

#-----------------------------------------------------------------------------#
pretime = time.time()
klines = client.get_historical_klines(token+asset, Client.KLINE_INTERVAL_1MINUTE,
                                      str(time.time()-(86400*data_days)))

open_price = list([float(i[1]) for i in klines])

print(str(time.time() - pretime))

for j in range(1, 61):
    return_sweep = []
    exchange_sweep = []  
    
    timeNOW = time.time();
    
    res_01 = tp.resistance(open_price, 315)
    sup_01 = tp.support(open_price, 315)
    res_trend = tp.resistance_trendline(open_price, 2880, 0.6)
    sup_trend = tp.support_trendline(open_price, 2880, 0.6)
    mov_dx = tp.derivative_ratio(open_price, 10)
    
    print(str(time.time() - timeNOW));
    
    for i in range(0, 101):        
        exchange_fee = 0.001
        risk_coeff = i/100
        
        funds = 10000
        funds_list = [funds]
        tokens = 0
        tokens_list = [(funds+tokens*open_price[0])] 
        value_list = [(funds, True)]
        
        exchange_price = []
        
        buy_val = 0
        sell_val = 0
        
        good_exchange_counter = 0
        bad_exchange_counter = 0        
                
        for x in range(1, len(open_price)):
            current_price = open_price[x]
            
            fund_check = int(funds*risk_coeff*100)/100
            token_sell = int(tokens*risk_coeff*100)/100
            
            token_buy = int((funds/current_price)*risk_coeff*100)/100
            value_check = int(risk_coeff*current_price*tokens*100)/100
            
            if(((current_price > res_trend[x] and (current_price > res_01[x]))            
                    ) and         
                    (fund_check > 10)): 
                buybool = True                       
                tokens = tokens + (1-exchange_fee)*token_buy                
                funds = funds - current_price*token_buy        
            elif((((current_price < sup_01[x]) and (current_price < sup_trend[x]))
                    or (mov_dx[x] >= 1 + (120/10000))
                    ) and 
                    (value_check > 10)):   
                buybool = False                
                funds = funds + (1-exchange_fee)*current_price*token_sell                
                tokens = tokens - risk_coeff*tokens       
            else:
                funds_list.append(funds)
                tokens_list.append(tokens)         
            if((funds+tokens*current_price)/value_list[x-1][0] == 1):
                value_list.append((funds+tokens*current_price, True))            
            else:
                value_list.append((funds+tokens*current_price, False))            
        print(str(i) +
              ": return = : " + 
              str(value_list[-1]/value_list[0]) +
              ", Funds: " + 
              str(funds) + 
              ", Tokens: " + 
              str(tokens))          
        return_sweep.append(value_list[-1]/value_list[0])        
       
      
#    li.append(sweep.index(max(sweep)))
#-----------------------------------------------------------------------------#
# Plotting and Visualization        
plt.plot(return_sweep)
plt.plot(exchange_sweep)
plt.plot(li)

plt.plot(open_price, color='orange')
plt.plot([x[0] for x in value_list[:]], color='black')

plt.plot(res_01, color='green')
plt.plot(sup_01, color='magenta')

plt.plot(res_trend, color='red')
plt.plot(sup_trend, color='blue')

plt.plot(mov_avg_01, color='cyan')

plt.plot(mov_dx, color='blue')

plt.plot(buy_marker, color='blue')
plt.plot(sell_marker, color='red')

plt.plot(top_range, color='blue')
plt.plot(bot_range, color='red')
plt.plot([top_range[i] - bot_range[i] for i in range(len(open_price))])

plt.plot(variance, color='blue')
    
#-----------------------------------------------------------------------------#
    # Statistical Model
        # Feature Generation
pred_int = 60 

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
A = np.array(open_price[:len(open_price)-pred_int], ndmin=2)
#-----------------------------------------------------------------------------#
    # Model Preprocessing
    
#Data Processing:
#x = A[max_interval:]
x = A
x = x.reshape((-1, 1))
                       
y = np.array(open_price[pred_int:], ndmin=2)
y = y.reshape((-1, 1))
#y = y[max_interval:]

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
batchSize = 1000 #len(x_test)
density_factor = 1
#
model = Sequential()
model.add(LSTM(100, return_sequences = True, activation = 'relu', unit_forget_bias=True, input_shape=(1, 1)))
model.add(Dropout(0.25))
model.add(LSTM(100, return_sequences = True, activation = 'relu', unit_forget_bias=True))
model.add(Dropout(0.25))
model.add(LSTM(100, return_sequences = False, activation = 'relu', unit_forget_bias=True))
model.add(Dropout(0.25))
model.add(Dense(100, activation = 'relu'))
model.add(Dropout(0.25))
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
model.fit(x_train, y_train, validation_split=0.33, epochs=40, batch_size=(batchSize), verbose=2, shuffle = False)


y_pred = model.predict(x_test)
plt.plot(y_test, color='black')
plt.plot(y_pred, color='cyan')

y_pred_train = model.predict(x_train)
plt.plot(y_train, color='orange')
plt.plot(y_pred_train, color='cyan')

pred_diff = [y_test[x] - y_pred[x] for x in range(len(y_test))]
plt.plot(pred_diff)

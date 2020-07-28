#!/usr/bin/env python
# coding: utf-8

# In[67]:


from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from sklearn.preprocessing import *
import numpy as np
import os
import matplotlib.pyplot as plt
import sklearn


# In[68]:pip


df = pd.read_excel(r'C:\Users\Raunak Karanjit\Desktop\project\dataset.xlsx', encoding='latin-1')
df.head()


# In[70]:


features = df[['hour', 'month', 'day', 'stationName']]


# In[71]:


stations = df['stationName'].unique()
days = sorted(df['day'].unique())

# Station encoding

new = pd.get_dummies(features, columns=["stationName","month","day"])
station_le = sklearn.preprocessing.LabelEncoder()
stations_int = station_le.fit_transform(stations)
station_ohe = sklearn.preprocessing.OneHotEncoder().fit(stations_int.reshape(-1, 1))

# Days encoding
days_le=  sklearn.preprocessing.LabelEncoder()
days_int = days_le.fit_transform(days)
days_ohe = sklearn.preprocessing.OneHotEncoder().fit(days_int.reshape(-1, 1))


# In[72]:


features.head()


# In[73]:


def create_feature(df):
    day_label_encoded = days_le.transform(df['day'])
    day_feature = days_ohe.transform(day_label_encoded.reshape(-1, 1)).toarray()
    station_label_encoded = station_le.transform(df['stationName'])
    station_feature = station_ohe.transform(station_label_encoded.reshape(-1, 1)).toarray()
    time_features = df[['hour', 'month']].values
    return np.concatenate([day_feature, time_features, station_feature], axis=1)


# In[74]:


def predict(X):
    df = pd.DataFrame([X], columns=['hour', 'month', 'day', 'stationName'])
    X = create_feature(df)
    return model.predict(X)[0]


# In[75]:


X = create_feature(features)


# In[76]:


Y = df['health_implication'].values


# In[77]:


model = RandomForestClassifier(random_state=42)


# In[78]:


model.fit(X, Y)


# In[79]:


model.score(X, Y)


# In[80]:


# hour, month, day, station
house = []

house = [j for j in df['hour'].unique()]
for l in df['hour'].unique():
    house[l]=predict([l, 11, 'Sunday', 'Ratna'])

plt.plot(df['hour'].unique(), house)
# naming the x axis
plt.xlabel('Time of the Day')
# naming the y axis
plt.ylabel('Air Quality Rating')

# giving a title to my graph
plt.title('Predicted Probability of Air Quality Rating over time for Ratnapark')

# function to show the plot
plt.show()
predict([0, 11, 'Sunday', 'Ratna'])

new_list = [j for j in range(10) for i in range(10)]


from numpy import array
from numpy import argmax
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
# define example
data = ['cold', 'cold', 'warm', 'cold', 'hot', 'hot', 'warm', 'cold', 'warm', 'hot']
values = array(data)
print(values)
# integer encode
label_encoder = LabelEncoder()
integer_encoded = label_encoder.fit_transform(values)
print(integer_encoded)
# binary encode
onehot_encoder = OneHotEncoder(sparse=False)
integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
onehot_encoded = onehot_encoder.fit_transform(integer_encoded)
print(onehot_encoded)
# invert first example
inverted = label_encoder.inverse_transform([argmax(onehot_encoded[0, :])])
print(inverted)

import pandas as pd
#Create a test dataframe
df = pd.DataFrame([
       ['green', 'Chevrolet', 2017],
       ['blue', 'BMW', 2015], 
       ['yellow', 'Lexus', 2018],
])
df.columns = ['color', 'make', 'year']


from sklearn.preprocessing import LabelEncoder
le_color = LabelEncoder()
le_make = LabelEncoder()
df['color_encoded'] = le_color.fit_transform(df.color)
df['make_encoded'] = le_make.fit_transform(df.make)

from sklearn.preprocessing import OneHotEncoder
color_ohe = OneHotEncoder()
make_ohe = OneHotEncoder()
X = color_ohe.fit_transform(df.color_encoded.values.reshape(-1,1)).toarray()
Xm = make_ohe.fit_transform(df.make_encoded.values.reshape(-1,1)).toarray()

X = color_ohe.fit_transform(df.color_encoded.values.reshape(1))

import numpy as py
a = py.matrix([[1, 2, 3, 4], [5, 6, 7, 8],[9,10,11,12]])
b = py.reshape(a, -1)

import numpy as np
from scipy.optimize import minimize
def rosen(x):
    '''The Rosenbrock function'''
    return sum(100.0*(x[1:]-x[:-1])**2.0+(1-x[:-1])**2.0)

x0 = np.array([1.3,0.7,0.8,1.9,1.2])
res = minimize(rosen, x0, method = 'nelder-mead',
               options={'xatol': 1e-8, 'disp':True})

def rosen_der(x):
    xm = x[1:-1]
    xm_m1 = x[:-2]
    xm_p1 = x[2:]
    der = np.zeros_like(x)
    der[1:-1] = 200*(xm-xm_m1**2)-400*(xm_p1 - xm**2)*xm - 2*(1-xm)
    der[0] = -400*x[0]*(x[1]-x[0]**2)-2*(1-x[0])
    der[-1] = 200*(x[-1]-x[-2]**2)
    return der

res = minimize(rosen, x0, method='BFGS', jac=rosen_der,
               options={'disp': True})
res.x
x = np.arange(6)
x = x.reshape((2,3))
print(x)
x = x.reshape((-1,1))
print(x)

from sympy import *
import math
x, y, z = symbols('x y z')
init_printing(use_unicode = True)

diff(math.cos(x),x)
diff(exp(x**2),x)

diff(integrate(exp(-x,0,oo),(x),x)

import matplotlib.pyplot as plt
%matplotlib inline
#creating the function and plotting it 

function = lambda x: (x ** 3)-(3 *(x ** 2))+7

#Get 1000 evenly spaced numbers between -1 and 3 (arbitratil chosen to ensure steep curve)
x = np.linspace(-1,3,500)

#Plot the curve
plt.plot(x, function(x))
plt.show()

def deriv(x):
    
    '''
    Description: This function takes in a value of x and returns its derivative based on the 
    initial function we specified.
    
    Arguments:
    
    x - a numerical value of x 
    
    Returns:
    
    x_deriv - a numerical value of the derivative of x
    
    '''
def deriv(x):  
    x_deriv = 3* (x**2) - (6 * (x))
    return x_deriv

def step(x_new, x_prev, precision, l_r): 
    
    x_list, y_list = [x_new], [function(x_new)]
    # keep looping until your desired precision
    while abs(x_new - x_prev) > precision:
        
        # change the value of x
        x_prev = x_new
        
        # get the derivation of the old value of x
        d_x = - deriv(x_prev)
        
        # get your new value of x by adding the previous, the multiplication of the derivative and the learning rate
        x_new = x_prev + (l_r * d_x)
        
        # append the new value of x to a list of all x-s for later visualization of path
        x_list.append(x_new)
        
        # append the new value of y to a list of all y-s for later visualization of path
        y_list.append(function(x_new))

    print ("Local minimum occurs at: "+ str(x_new))
    print ("Number of steps: " + str(len(x_list)))
    

    plt.subplot(1,2,2)
    plt.scatter(x_list,y_list,c="g")
    plt.plot(x_list,y_list,c="g")
    plt.plot(x,function(x), c="r")
    plt.title("Gradient descent")
    plt.show()

    plt.subplot(1,2,1)
    plt.scatter(x_list,y_list,c="g")
    plt.plot(x_list,y_list,c="g")
    plt.plot(x,function(x), c="r")
    plt.xlim([1.0,2.1])
    plt.title("Zoomed in Gradient descent to Key Area")
    plt.show()

step(0.0001, 0, 0.001, 0.05)

import numpy as np
from sklearn.linear_model import LinearRegression
x = np.array([5, 15, 25, 35, 45, 55]).reshape((-1, 1))
y = np.array([5, 20, 14, 32, 22, 38])
model = LinearRegression()
model.fit(x,y)
model = LinearRegression().fit(x,y)
r_sq = model.score(x,y)
print('intercept:', model.intercept_)
print('slope:', model.coef_)
y_pred = model.predict(x)
print('predicted response:', y_pred, sep = '\n')
x = [[0, 1], [5, 1], [15, 2], [25, 5], [35, 11], [45, 15], [55, 34], [60, 35]]
y = [4, 5, 20, 14, 32, 22, 38, 43]
x, y = np.array(x), np.array(y)
model = LinearRegression().fit(x,y)
r_sq = model.score(x,y)





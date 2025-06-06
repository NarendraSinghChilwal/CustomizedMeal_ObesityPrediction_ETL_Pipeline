#!/usr/bin/env python
# coding: utf-8

# In[101]:


import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.svm import SVC
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


# In[102]:


df = pd.read_csv("C:\\Users\\ADMIN\\OneDrive\\Desktop\\obesity_level.csv")
df


# # BUSINESS UNDERSTANDING:
# 
# Objective:
# To classify individuals into obesity levels based on lifestyle, dietary habits, and physical activity. The goal is to build a predictive model and identify key factors contributing to obesity in Mexico, Peru, and Colombia.
# 
# Key Questions:
# 1) What features most influence obesity levels?  
# 2) How accurately can we classify individuals into obesity categories?  
# 

# #DATA INFORMATION:
# 
# The data contains 19 attributes and 2111 records.
# 
# Gender is 1 if a respondent is male and 0 if a respondent is female.
# 
# Age is a respondent’s age in years.
# 
# family_history_with_overweight is 1 if a respondent has family member who is or was overweight, 0 if not.
# 
# FAVC is 1 if a respondent eats high caloric food frequently, 0 if not.
# 
# FCVC is 1 if a respondent usually eats vegetables in their meals, 0 if not.
# 
# NCP represents how many main meals a respondent has daily (0 for 1-2 meals, 1 for 3 meals, and 2 for more than 3 meals).
# 
# CAEC represents how much food a respondent eats between meals on a scale of 0 to 3.
# 
# SMOKE is 1 if a respondent smokes, 0 if not.
# 
# CH2O represents how much water a respondent drinks on a scale of 0 to 2.
# 
# SCC is 1 if a respondent monitors their caloric intake, 0 if not.
# 
# FAF represents how much physical activity a respondent does on a scale of 0 to 3.
# 
# TUE represents how much time a respondent spends looking at devices with screens on a scale of 0 to 2.
# 
# CALC represents how often a respondent drinks alcohol on a scale of 0 to 3.
# 
# MTRANS : Feature, Categorical, " Which transportation do you usually use? 
# 
# NObeyesdad is a 1 if a patient is obese and a 0 if not.

# In[105]:


df.columns


# In[106]:


df.rename(columns={
    'id': 'id',
    'Gender': 'gender',
    'Age': 'age',
    'Height': 'height',
    'Weight': 'weight',
    'family_history_with_overweight': 'fam_hist_ow',
    'FAVC': 'high_cal_food',
    'FCVC': 'veg_meals',
    'NCP': 'main_meals',
    'CAEC': 'snack_freq',
    'SMOKE': 'smokes',
    'CH2O': 'water_intake',
    'SCC': 'calorie_monitor',
    'FAF': 'phys_activity',
    'TUE': 'screen_time',
    'CALC': 'alcohol_freq',
    'MTRANS': 'transport_mode',
    '0be1dad': 'obesity_level'
}, inplace=True)


# # Exploratory Data Analysis

# In[108]:


df.isna().sum()


# In[109]:


numeric_attributes = df.select_dtypes(include=[np.number]).columns

# Visualize the distribution of numerical attributes using boxplots
plt.figure(figsize=(20, 15))
for i, col in enumerate(numeric_attributes, 1):
    plt.subplot(4, 4, i)  # Adjusted subplot dimensions to accommodate all numerical attributes
    sns.boxplot(data=df, y=col)
    plt.tight_layout()
plt.show()


# In[110]:


#Check relationship between different attributes and Obesity level(y)
plt.figure(figsize=(20, 15))
for i, col in enumerate(numeric_attributes, 1):
    plt.subplot(4, 4, i)
    sns.boxplot(data=df, x='obesity_level', y=col)
    plt.xticks(rotation=45)
    plt.tight_layout()
plt.show()


# In[111]:


# Calculate and visualize the correlation matrix for numerical attributes
plt.figure(figsize=(10, 8))
sns.heatmap(df[numeric_attributes].corr(), annot=True, fmt=".2f", cmap='coolwarm')
plt.show()


# # Data Preparation

# In[113]:


# Encoding categorical variables using Label Encoding
label_encoders = {}
for column in ['gender', 'snack_freq', 'alcohol_freq', 'transport_mode']:
    le = LabelEncoder()
    df[column] = le.fit_transform(df[column])
    label_encoders[column] = le


# In[114]:


#Normalizing numerical attribute
numerical_columns = [
    'age', 'height', 'weight', 'fam_hist_ow', 
    'high_cal_food', 'veg_meals', 'main_meals', 
    'smokes', 'water_intake', 'calorie_monitor', 
    'phys_activity', 'screen_time'
]
scaler = StandardScaler()
df[numerical_columns] = scaler.fit_transform(df[numerical_columns])


# In[115]:


# Splitting the data
X = df.drop(['obesity_level', 'id'], axis=1)  # Excluding 'id' and target variable
y = df['obesity_level']  # Target variable

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=23316144)


# # MODELLING:
# 
# 1) Random Forest

# In[117]:


# Initialize the RandomForest model
model = RandomForestClassifier(random_state=23316144)

# Train the RandomForest model
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluate the RandomForest model
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')
auc = roc_auc_score(y_test, model.predict_proba(X_test), multi_class='ovr', average='weighted')

print(f"RandomForest Performance:\nAccuracy: {accuracy}\nPrecision: {precision}\nRecall: {recall}\nF1 Score: {f1}\nAUC-ROC: {auc}")


# 2) Support Vector Machine

# In[119]:


# Initialize the SVM model
model = SVC(probability=True, random_state=23316144)

# Train the SVM model
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluate the SVM model
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')
auc = roc_auc_score(y_test, model.predict_proba(X_test), multi_class='ovr', average='weighted')

print(f"SVM Performance:\nAccuracy: {accuracy}\nPrecision: {precision}\nRecall: {recall}\nF1 Score: {f1}\nAUC-ROC: {auc}")


# In[ ]:





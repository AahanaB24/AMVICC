import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

 #inspects to make sure it loads correctly
#DALLE3
df = pd.read_csv('dalle3_grades.csv')
#Checking Totals for Each Category
print("Dalle3 Results")
#individual grading:
categories = ['ca', 'od', 'pf', 'pr', 'qc', 'sc', 'sh', 'tx', 'vp']
counter = 0
totals = ['', '', '', '', '', '', '', '', '',]
total_correct_im = ['', '', '', '', '', '', '', '', '',]
total_correct_ex = ['', '', '', '', '', '', '', '', '',]
accuracy_im = ['', '', '', '', '', '', '', '', '',]
accuracy_ex = ['', '', '', '', '', '', '', '', '',]
for category in categories:
    subset = df[df['Category'] == category]
    total = len(subset)
    totals[counter] = total
    correct_subset_im = subset[subset['Correct_im'] == 'Y']
    correct_subset_ex = subset[subset['Correct_ex'] =='Y']
    total_correct_im[counter] = len(correct_subset_im)
    total_correct_ex[counter] = len(correct_subset_ex)
    accuracy_im[counter] = total_correct_im[counter]/total
    accuracy_ex[counter] = total_correct_ex[counter]/total
    counter += 1


#Pairs Grading:
counter = 0
pair_totals = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
pair_total_correct_im = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
pair_total_correct_ex = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
pair_accuracy_im = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
pair_accuracy_ex = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
for category in categories:
    subset = df[df['Category'] == category].reset_index()

    total = len(subset)/2
    for index in range(0, len(subset), 2): 
        pair_totals[counter] = pair_totals[counter] + 1
        if subset["Correct_im"][index] == 'Y' and subset["Correct_im"][index + 1] == 'Y':
            pair_total_correct_im[counter] = pair_total_correct_im[counter] + 1
        if subset["Correct_ex"][index] == 'Y' and subset["Correct_ex"][index + 1] == 'Y':
            pair_total_correct_ex[counter] = pair_total_correct_ex[counter] + 1
    
    pair_accuracy_im[counter] = pair_total_correct_im[counter]/(total)
    pair_accuracy_ex[counter] = pair_total_correct_ex[counter]/(total)
    counter += 1

data_dalle3= {
    "Categories": categories,
    "I Im": accuracy_im,
    "I Ex": accuracy_ex,
    "P Im": pair_accuracy_im,
    "P Ex": pair_accuracy_ex,
}
print("Dalle 3")
df_dalle3 = pd.DataFrame(data_dalle3)
print(df_dalle3)

#GOOGLE FLASH
df = pd.read_csv('google_flash_grades.csv')
#Checking Totals for Each Category
print("Google Flash Results")
#individual grading:
categories = ['ca', 'od', 'pf', 'pr', 'qc', 'sc', 'sh', 'tx', 'vp']
counter = 0
totals = ['', '', '', '', '', '', '', '', '',]
total_correct_im = ['', '', '', '', '', '', '', '', '',]
total_correct_ex = ['', '', '', '', '', '', '', '', '',]
accuracy_im = ['', '', '', '', '', '', '', '', '',]
accuracy_ex = ['', '', '', '', '', '', '', '', '',]
for category in categories:
    subset = df[df['Category'] == category]
    total = len(subset)
    totals[counter] = total
    correct_subset_im = subset[subset['Correct_im'] == 'Y']
    correct_subset_ex = subset[subset['Correct_ex'] =='Y']
    total_correct_im[counter] = len(correct_subset_im)
    total_correct_ex[counter] = len(correct_subset_ex)
    accuracy_im[counter] = total_correct_im[counter]/total
    accuracy_ex[counter] = total_correct_ex[counter]/total
    counter += 1


#Pairs Grading:
counter = 0
pair_totals = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
pair_total_correct_im = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
pair_total_correct_ex = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
pair_accuracy_im = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
pair_accuracy_ex = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
for category in categories:
    subset = df[df['Category'] == category].reset_index()

    total = len(subset)/2
    for index in range(0, len(subset), 2): 
        pair_totals[counter] = pair_totals[counter] + 1
        if subset["Correct_im"][index] == 'Y' and subset["Correct_im"][index + 1] == 'Y':
            pair_total_correct_im[counter] = pair_total_correct_im[counter] + 1
        if subset["Correct_ex"][index] == 'Y' and subset["Correct_ex"][index + 1] == 'Y':
            pair_total_correct_ex[counter] = pair_total_correct_ex[counter] + 1
    
    pair_accuracy_im[counter] = pair_total_correct_im[counter]/(total)
    pair_accuracy_ex[counter] = pair_total_correct_ex[counter]/(total)
    counter += 1

data_gf = {
    "Categories": categories,
    "I Im": accuracy_im,
    "I Ex": accuracy_ex,
    "P Im": pair_accuracy_im,
    "P Ex": pair_accuracy_ex,
}
print("Google Flash")
df_gf = pd.DataFrame(data_gf)
print(df_gf)
 #inspects to make sure it loads correctly

#STABLE DIFFUSION
df = pd.read_csv("stable_diff_grades.csv")
#Checking Totals for Each Category
print("Stable Diffusion Results")
#individual grading:
categories = ['ca', 'od', 'pf', 'pr', 'qc', 'sc', 'sh', 'tx', 'vp']
counter = 0
totals = ['', '', '', '', '', '', '', '', '',]
total_correct_im = ['', '', '', '', '', '', '', '', '',]
total_correct_ex = ['', '', '', '', '', '', '', '', '',]
accuracy_im = ['', '', '', '', '', '', '', '', '',]
accuracy_ex = ['', '', '', '', '', '', '', '', '',]
for category in categories:
    subset = df[df['Category'] == category]
    total = len(subset)
    totals[counter] = total
    correct_subset_im = subset[subset['Correct_im'] == 'Y']
    correct_subset_ex = subset[subset['Correct_ex'] =='Y']
    total_correct_im[counter] = len(correct_subset_im)
    total_correct_ex[counter] = len(correct_subset_ex)
    accuracy_im[counter] = total_correct_im[counter]/total
    accuracy_ex[counter] = total_correct_ex[counter]/total
    counter += 1


#Pairs Grading:
counter = 0
pair_totals = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
pair_total_correct_im = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
pair_total_correct_ex = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
pair_accuracy_im = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
pair_accuracy_ex = [0, 0, 0, 0, 0, 0, 0, 0, 0,]
for category in categories:
    subset = df[df['Category'] == category].reset_index()

    total = len(subset)/2
    for index in range(0, len(subset), 2): 
        pair_totals[counter] = pair_totals[counter] + 1
        if subset["Correct_im"][index] == 'Y' and subset["Correct_im"][index + 1] == 'Y':
            pair_total_correct_im[counter] = pair_total_correct_im[counter] + 1
        if subset["Correct_ex"][index] == 'Y' and subset["Correct_ex"][index + 1] == 'Y':
            pair_total_correct_ex[counter] = pair_total_correct_ex[counter] + 1
    
    pair_accuracy_im[counter] = pair_total_correct_im[counter]/(total)
    pair_accuracy_ex[counter] = pair_total_correct_ex[counter]/(total)
    counter += 1

data_sd = {
    "Categories": categories,
    "I Im": accuracy_im,
    "I Ex": accuracy_ex,
    "P Im": pair_accuracy_im,
    "P Ex": pair_accuracy_ex,
}
print("Stable Diffusion")
df_sd = pd.DataFrame(data_sd)
print(df_sd)


data = {
    "Category": categories, 
    "Accuracy Implicit": pair_accuracy_im, 
    "Accuracy Explicit": pair_accuracy_ex, 
}
df_figures = pd.DataFrame(data)
print("Figures: ")
print("Scatterplot")
print(df_figures)



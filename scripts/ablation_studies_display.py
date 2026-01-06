import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

#Ablation Studies - Prompt Wording
df = pd.read_csv('dalle3_wording_ab.csv')
#Checking Totals for Each Category
print("Wording Ablation Study Results")
#individual grading:
categories = ['ca','pf','pr','sc', 'sh','tx']
counter = 0
totals = ['', '', '', '', '', '']
total_correct_im = ['', '', '', '', '', '']
total_correct_ex = ['', '', '', '', '', '']
accuracy_im = ['', '', '', '', '', '']
accuracy_ex = ['', '', '', '', '', '']
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
pair_totals = [0, 0, 0, 0, 0, 0]
pair_total_correct_im = [0, 0, 0, 0, 0, 0]
pair_total_correct_ex = [0, 0, 0, 0, 0, 0]
pair_accuracy_im = [0, 0, 0, 0, 0, 0]
pair_accuracy_ex = [0, 0, 0, 0, 0, 0]
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

data_dalle3_wording= {
    "Categories": categories,
    "I Im": accuracy_im,
    "I Ex": accuracy_ex,
    "P Im": pair_accuracy_im,
    "P Ex": pair_accuracy_ex,
}
print("Wording")
df_wording = pd.DataFrame(data_dalle3_wording)
print(df_wording)


#Ablation Studies - Normal
df = pd.read_csv('dalle3_normalab.csv')
#Checking Totals for Each Category
print("Normal Results")
#individual grading:
counter = 0
totals = ['', '', '', '', '', '']
total_correct_im = ['', '', '', '', '', '']
total_correct_ex = ['', '', '', '', '', '']
accuracy_im = ['', '', '', '', '', '']
accuracy_ex = ['', '', '', '', '', '']
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
pair_totals = [0, 0, 0, 0, 0, 0]
pair_total_correct_im = [0, 0, 0, 0, 0, 0]
pair_total_correct_ex = [0, 0, 0, 0, 0, 0]
pair_accuracy_im = [0, 0, 0, 0, 0, 0]
pair_accuracy_ex = [0, 0, 0, 0, 0, 0]
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

data_dalle3_normal= {
    "Categories": categories,
    "I Im": accuracy_im,
    "I Ex": accuracy_ex,
    "P Im": pair_accuracy_im,
    "P Ex": pair_accuracy_ex,
}
print("Normal")
df_dalle3 = pd.DataFrame(data_dalle3_normal)
print(df_dalle3)

df_combined = pd.DataFrame({
    "Categories": categories, 
    "Pair Im (C)": data_dalle3_normal["P Im"],
    "Pair Im (W)": data_dalle3_wording["P Im"],
    "Pair Ex (C)": data_dalle3_normal["P Ex"],
    "Pair Ex (W)": data_dalle3_wording["P Ex"],
})
print("Combined")
print(df_combined)


#Ablation Studies - Randomness
df = pd.read_csv('dalle3_randomness.csv')
#Checking Totals for Each Category
print("Randomess Results")
df_split = np.array_split(df, 3)
df1 = df_split[0].reset_index()
df2 = df_split[1].reset_index()
df3 = df_split[2].reset_index()

tests = ["test_1", "test_2", "test_3"]

df_randomness = pd.DataFrame({
    "Columns": ["Test 1", "Test 2", "Test 3"], 
    "Totals": [0, 0, 0],
    "Total Correct Im": [0, 0, 0],
    "Total Correct Ex": [0, 0, 0],
    "Accuracy Im": [0, 0, 0],
    "Accuracy Ex": [0, 0, 0],
    "Pair Totals": [0, 0, 0],
    "Pair Total Correct Im": [0, 0, 0],
    "Pair Total Correct Ex": [0, 0, 0],
    "Pair Accuracy Im": [0, 0, 0],
    "Pair Accuracy Ex": [0, 0, 0],
})
print(df_randomness)
counter = 0
#individual grading:
for i, df_test in enumerate(df_split): 
    total = len(df_test)
    df_randomness.loc[i, "Totals"] = total
    
    # Fix: Use .sum() instead of len() for boolean filtering
    df_randomness.loc[i, "Total Correct Im"] = (df_test["Correct_im"] == "Y").sum()
    df_randomness.loc[i, "Total Correct Ex"] = (df_test["Correct_ex"] == "Y").sum()
    
    # Fix: Calculate both accuracies correctly
    df_randomness.loc[i, "Accuracy Im"] = df_randomness.loc[i, "Total Correct Im"] / total
    df_randomness.loc[i, "Accuracy Ex"] = df_randomness.loc[i, "Total Correct Ex"] / total
    
    # Pairs Grading:
    df_temp = df_test.reset_index(drop=True)  # Fix: drop=True to avoid index column
    pair_total = len(df_temp) // 2  # Fix: Use integer division
    df_randomness.loc[i, "Pair Totals"] = pair_total
    
    pair_correct_im = 0
    pair_correct_ex = 0
    
    for index in range(0, len(df_temp), 2): 
        if index + 1 < len(df_temp):  # Safety check
            if df_temp["Correct_im"].iloc[index] == 'Y' and df_temp["Correct_im"].iloc[index + 1] == 'Y':
                pair_correct_im += 1
            if df_temp["Correct_ex"].iloc[index] == 'Y' and df_temp["Correct_ex"].iloc[index + 1] == 'Y':
                pair_correct_ex += 1
    
    df_randomness.loc[i, "Pair Total Correct Im"] = pair_correct_im
    df_randomness.loc[i, "Pair Total Correct Ex"] = pair_correct_ex
    
    # Fix: Calculate pair accuracy correctly
    if pair_total > 0:
        df_randomness.loc[i, "Pair Accuracy Im"] = pair_correct_im / pair_total
        df_randomness.loc[i, "Pair Accuracy Ex"] = pair_correct_ex / pair_total

data_dalle3_randomness= {
    "Tests": df_randomness["Columns"],
    "I Im": df_randomness["Accuracy Im"],
    "I Ex": df_randomness["Accuracy Ex"],
    "P Im": df_randomness["Pair Accuracy Im"],
    "P Ex": df_randomness["Pair Accuracy Ex"],
}
print("Randomness")
df_dalle3_rand = pd.DataFrame(data_dalle3_randomness)
print(df_dalle3_rand)



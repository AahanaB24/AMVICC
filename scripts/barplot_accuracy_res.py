import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_style("whitegrid") 
plt.rcParams['font.family'] ='serif' 
plt.rcParams['font.size'] = 2

df_mtaccuracy = pd.DataFrame({
    "Models": ["GPT-4o", "Gemini", "Qwen", "Pixtral", "Grok 4", "Gemma", 
               "Llama 3.2", "Maverick", "Scout", "Opus", "Sonnet 4"],
    "Accuracy": [71.33, 70, 64, 62, 44, 56, 85.33, 77.33, 72, 69.33, 57.33]
})

df_mtaccuracy = df_mtaccuracy.sort_values('Accuracy', ascending=False).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(1, 1), dpi=300)

bars = sns.barplot(data=df_mtaccuracy, y='Models', x='Accuracy', 
                   palette='viridis', ax=ax)

ax.set_xlabel("Accuracy (%)", fontsize=2, labelpad=-.1)
ax.set_ylabel("") 

for i, bar in enumerate(bars.patches):
    width = bar.get_width()
    ax.text(width + 0.5,  
            bar.get_y() + bar.get_height()/2.,
            f'{width:.0f}', 
            ha='left', va='center',
            fontsize=2, 
            color='black') 


ax.tick_params(axis='both', which='major', labelsize=2)
ax.tick_params(axis='x', which='major', labelsize=2)

ax.set_xlim(40, 90)  

for spine in ax.spines.values():
    spine.set_visible(False)
ax.spines['bottom'].set_visible(True)


ax.set_xticks([60, 70, 80, 90])
ax.set_xticklabels(['60', '70', '80', '90'])
ax.tick_params(axis='x', which='major', labelsize=2, pad=-2)
ax.tick_params(axis='y', which='major', pad=2)

plt.subplots_adjust(left=0.25, right=0.98, top=0.98)

plt.show()
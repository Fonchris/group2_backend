import json
import pandas as pd

# Load the JSON file
with open('single_words.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract the vocabulary list
vocabulary = data['vocabulary']

# Create a DataFrame
df = pd.DataFrame(vocabulary)

# Reorder columns to match your requested order
df = df[['french', 'english', 'fulfulde']]

# Save to Excel with your specified filename
output_filename = 'single_word_fulfulde.xlsx'
df.to_excel(output_filename, index=False)  # Removed the encoding parameter

print(f"Excel file '{output_filename}' has been created successfully!")
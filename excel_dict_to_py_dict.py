import pandas as pd
import json

def extract_translation_dictionaries(excel_file_path):
    """
    Extract translation data from an Excel file and create dictionaries.
    
    Args:
        excel_file_path (str): Path to the Excel file containing translation data
        
    Returns:
        dict: Dictionary containing language pairs and their translations
    """
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file_path)
        
        # Check if the dataframe has the expected columns
        if len(df.columns) < 3:
            raise ValueError(f"Expected at least 3 columns, found {len(df.columns)}")
        
        # Extract column names (languages)
        languages = df.iloc[0].tolist()
        
        # Clean language names
        languages = [str(lang).strip().lower() for lang in languages if pd.notna(lang)]
        
        # Create dictionaries for each language pair
        dictionaries = {}
        
        # Create English-Ghomala dictionary
        eng_ghomala = {}
        for _, row in df.iloc[1:].iterrows():
            eng_term = row.iloc[0]
            ghomala_term = row.iloc[2]
            
            # Skip rows with missing data
            if pd.isna(eng_term) or pd.isna(ghomala_term):
                continue
                
            eng_term = str(eng_term).strip()
            ghomala_term = str(ghomala_term).strip()
            
            if eng_term and ghomala_term:
                eng_ghomala[eng_term] = ghomala_term
                
        dictionaries['english-ghomala'] = eng_ghomala
        
        # Create French-Ghomala dictionary
        fr_ghomala = {}
        for _, row in df.iloc[1:].iterrows():
            fr_term = row.iloc[1]
            ghomala_term = row.iloc[2]
            
            # Skip rows with missing data
            if pd.isna(fr_term) or pd.isna(ghomala_term):
                continue
                
            fr_term = str(fr_term).strip()
            ghomala_term = str(ghomala_term).strip()
            
            if fr_term and ghomala_term:
                fr_ghomala[fr_term] = ghomala_term
                
        dictionaries['french-ghomala'] = fr_ghomala
        
        return dictionaries
        
    except Exception as e:
        print(f"Error extracting translation data: {e}")
        return {}

def save_dictionaries_to_py(dictionaries, output_file_path):
    """
    Save the dictionaries to a Python file in the required format
    
    Args:
        dictionaries (dict): Dictionary containing language pairs and translations
        output_file_path (str): Path to save the output Python file
    """
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write("TEMPORARY_DICTIONARIES = {\n")
            
            for i, (lang_pair, translations) in enumerate(dictionaries.items()):
                f.write(f"    '{lang_pair}': {{\n")
                
                for j, (source, target) in enumerate(translations.items()):
                    comma = "," if j < len(translations) - 1 else ""
                    f.write(f'        "{source}": "{target}"{comma}\n')
                
                comma = "," if i < len(dictionaries) - 1 else ""
                f.write(f"    }}{comma}\n")
                
            f.write("}\n")
            
        print(f"Dictionaries successfully saved to {output_file_path}")
        
    except Exception as e:
        print(f"Error saving dictionaries to file: {e}")

def main():
    # File paths
    excel_file_path = "./Ghomala-datasets/EN_FR_Ghomala_DICTIONARY.xlsx"  # Replace with your Excel file path
    output_file_path = "translation_dictionaries.py"
    
    # Extract dictionaries from Excel
    dictionaries = extract_translation_dictionaries(excel_file_path)
    
    if dictionaries:
        # Save dictionaries to Python file
        save_dictionaries_to_py(dictionaries, output_file_path)
        
        # Display dictionaries in console
        print("\nExtracted Dictionaries:")
        print(json.dumps(dictionaries, indent=4, ensure_ascii=False))
    else:
        print("Failed to extract dictionaries from the Excel file.")

if __name__ == "__main__":
    main()
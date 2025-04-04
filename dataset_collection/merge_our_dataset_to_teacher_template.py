import pandas as pd

def merge_translations(template_file, translations_file, output_file):
    """
    Merges Ghomala translations from a translations file into a template file.

    Args:
        template_file (str): Path to the template Excel file (English, French, Ghomala - Ghomala may be empty).
        translations_file (str): Path to the Excel file containing translations (English, French, Ghomala).
        output_file (str): Path to save the merged Excel file.
    """
    try:
        template_df = pd.read_excel(template_file)
        # Explicitly set the Ghomala column type to string
        template_df["Ghomala"] = template_df["Ghomala"].astype(str).replace('nan', pd.NA)
        translations_df = pd.read_excel(translations_file)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return
    except Exception as e:
        print(f"Error reading Excel files: {e}")
        return

    # *** IMPORTANT: ADJUST THESE COLUMN NAMES IF THEY ARE DIFFERENT IN YOUR FILES ***
    required_cols = ["English", "French", "Ghomala"]
    for col in required_cols:
        if col not in template_df.columns or col not in translations_df.columns:
            print(f"Error: Both files must contain columns: {required_cols}")
            print(f"Template Columns: {template_df.columns.tolist()}")
            print(f"Translations Columns: {translations_df.columns.tolist()}")
            return

    merged_df = template_df.copy()

    translation_dict = translations_df.set_index("English")["Ghomala"].to_dict()
    french_dict = translations_df.set_index("English")["French"].to_dict()

    for index, row in merged_df.iterrows():
        english_word = row["English"]
        if english_word in translation_dict and pd.isna(row["Ghomala"]):
            merged_df.loc[index, "Ghomala"] = translation_dict[english_word]
        elif english_word in translation_dict and row["French"] != french_dict.get(english_word):
            print(f"Warning: French translation mismatch for '{english_word}'. Template: '{row['French']}', Translations file: '{french_dict.get(english_word)}'. Keeping template's Ghomala if present.")

    new_entries_df = translations_df[~translations_df["English"].isin(merged_df["English"])].copy()
    # Ensure new entries also have Ghomala as string type
    if "Ghomala" in new_entries_df.columns:
        new_entries_df["Ghomala"] = new_entries_df["Ghomala"].astype(str)

    merged_df = pd.concat([merged_df, new_entries_df], ignore_index=True)
    merged_df.drop_duplicates(subset=["English", "French"], keep='first', inplace=True)

    try:
        merged_df.to_excel(output_file, index=False)
        print(f"Merged data saved to '{output_file}'")
    except Exception as e:
        print(f"Error saving the merged data to Excel: {e}")

if __name__ == "__main__":
   
    template_file = "C:/Users/AFC/PycharmProjects/no_name_for_now_dataset/Ghomala-datasets/dictionary_template_eng_fre_ghomala.xlsx"
    translations_file = "C:/Users/AFC/PycharmProjects/no_name_for_now_dataset/Ghomala-datasets/EN_FR_Ghomala_DICTIONARY.xlsx"
    output_file = "merged_dictionary_ghomala.xlsx"

    merge_translations(template_file, translations_file, output_file)
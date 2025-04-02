import pandas as pd
import deepl
import time

# === CONFIG ===
EXCEL_FILE_PATH = "C:/Users/AFC/PycharmProjects/no_name_for_now_dataset/english-fulfulde.xlsx"  # Your input file
OUTPUT_FILE_PATH = "english-french-fulfulde.xlsx"  # Output file
DEEPL_API_KEY = "your-api-key"  # Replace with your actual API key

# === Initialize DeepL Translator ===
translator = deepl.Translator(DEEPL_API_KEY)

def translate_to_french(english_text, retries=3):
    """Translates English to French using DeepL API with retries."""
    for attempt in range(retries):
        try:
            result = translator.translate_text(english_text, source_lang="EN", target_lang="FR")
            return result.text
        except Exception as e:
            print(f"Attempt {attempt + 1}: Error translating '{english_text}': {e}")
            time.sleep(1)  # Wait before retrying
    return english_text  # Return original if translation fails

def clean_and_translate_excel(input_path, output_path):
    """Cleans duplicates and translates English to French, then saves to Excel."""
    
    # === Load Excel file ===
    df = pd.read_excel(input_path)

    # === Validate Columns ===
    required_columns = ["English", "Fulfulde"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Excel file must contain columns: {required_columns}")

    # === Remove duplicates ===
    df = df.drop_duplicates(subset=["English"], keep="first").reset_index(drop=True)

    # === Translate English to French ===
    df["French"] = df["English"].apply(translate_to_french)

    # === Save cleaned & translated data ===
    df.to_excel(output_path, index=False)
    print(f"✅ Cleaning & translation complete! File saved as {output_path}")

# === Run the script ===
clean_and_translate_excel(EXCEL_FILE_PATH, OUTPUT_FILE_PATH)

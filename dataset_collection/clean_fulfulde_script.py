import pandas as pd

def clean_dataset(excel_file_path):
    """
    Cleans an Excel dataset with "English", "French", and "Fulfulde" columns.
    Removes duplicates and handles cells with multiple words separated by
    either '/' or ',' in the 'Fulfulde' column.

    Args:
        excel_file_path (str): The full path to the Excel file.

    Returns:
        pandas.DataFrame: The cleaned DataFrame, or None if an error occurs.
    """
    try:
        df = pd.read_excel(excel_file_path)
    except FileNotFoundError:
        print(f"Error: File not found at '{excel_file_path}'")
        return None
    except Exception as e:
        print(f"Error reading the Excel file '{excel_file_path}': {e}")
        return None

    # Check if the required columns exist (using the correct capitalization)
    required_columns = ["English", "French", "Fulfulde"]
    if not all(col in df.columns for col in required_columns):
        print(f"Error: The Excel file '{excel_file_path}' must contain columns named '{', '.join(required_columns)}'.")
        print(f"Actual columns found: {df.columns.tolist()}")  # Print actual columns for debugging
        return None

    # Remove duplicate rows
    initial_rows = len(df)
    df.drop_duplicates(inplace=True)
    duplicates_removed = initial_rows - len(df)
    if duplicates_removed > 0:
        print(f"Removed {duplicates_removed} duplicate rows from '{excel_file_path}'.")

    # Clean the 'Fulfulde' column for cells with multiple words separated by '/' or ','
    def clean_fulfulde_cell(cell):
        if isinstance(cell, str):
            if "/" in cell:
                words = cell.split("/")
                if len(words) == 2:
                    return words[0].strip()  # Keep the first word after '/'
            elif "," in cell:
                words = cell.split(",")
                if len(words) == 2:
                    return words[0].strip()  # Keep the first word after ','
        return cell

    df['Fulfulde'] = df['Fulfulde'].apply(clean_fulfulde_cell)

    print(f"Dataset cleaning complete for '{excel_file_path}'.")
    return df

if __name__ == "__main__":
    input_file_path = r"C:\Users\AFC\PycharmProjects\no_name_for_now_dataset\Fulfulde-datasets\EN_FR_Fulfulde_DC_DICTIONARY.xlsx"
    output_file_name = "cleaned_data_updated.xlsx"

    cleaned_df = clean_dataset(input_file_path)

    if cleaned_df is not None:
        try:
            cleaned_df.to_excel(output_file_name, index=False)
            print(f"Cleaned data saved to '{output_file_name}'")
        except Exception as e:
            print(f"Error saving the cleaned data to Excel: {e}")
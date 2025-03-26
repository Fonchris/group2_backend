import json

# Define file paths
input_json_path = "french-ghomala-bandjoun.json"  # Replace with your JSON file path
output_json_path = "single-word-ghomala_french_dictionary.json"  # Output file for dictionary


def filter_single_word_entries(input_path, output_path):
    """Filters and extracts entries where Ghomala has only one word."""

    # Read input JSON file
    with open(input_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Filter entries where Ghomala contains only one word (no spaces)
    filtered_data = [
        {"ghomala": entry["ghomala"], "francais": entry["francais"]}
        for entry in data
        if entry.get("ghomala") and len(entry["ghomala"].split()) == 1
    ]

    # Save the filtered dictionary as JSON
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(filtered_data, file, ensure_ascii=False, indent=4)

    print(f"Filtered dictionary saved to {output_path}. {len(filtered_data)} entries found.")


# Run the function
filter_single_word_entries(input_json_path, output_json_path)

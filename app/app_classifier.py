import os
import json

def _create_initial_json_file(file_path):
    """
    Helper function to create an initial, empty JSON file with the expected structure.
    """
    initial_data = {
        "productivity_app": [],
        "entertainment_app": []
    }
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=4, ensure_ascii=False)
        print(f"Info: '{file_path}' not found. Created an empty file with initial structure.")
    except IOError as e:
        print(f"Error: Could not create '{file_path}'. Reason: {e}")
        # Re-raise the exception or handle appropriately if file creation is critical
        # For now, we'll let the main function attempt to proceed, but it will likely fail
        # if the file couldn't be created.

def classify_app_or_website(app_name, categories_file_path="productivity.json"):
    """
    Classifies an application or website name as 'Productive' or 'Entertainment'
    based on keywords found in a specified JSON file (e.g., productivity.json).
    If the file does not exist, it will be created with an empty structure.

    Args:
        app_name (str): The name of the application or website to classify.
        categories_file_path (str): The path to the JSON file containing classification keywords.
                                    Defaults to 'productivity.json'.

    Returns:
        str: A message indicating the classification, or an error/not found message.
    """
    productive_keywords = []
    entertainment_keywords = []

    # The file creation/check is now handled at the start of the __main__ block
    # so we assume it exists and is properly initialized at this point.
    # However, we still need to handle cases where it might be empty or corrupted *after* creation.

    try:
        # Check if the file is empty before loading JSON
        if os.path.getsize(categories_file_path) == 0:
            print(f"Warning: '{categories_file_path}' is empty. Initializing its content.")
            _create_initial_json_file(categories_file_path) # Re-initialize if found empty

        with open(categories_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f) # Load the JSON data from the file

            # Extract keywords from 'productivity_app' and 'entertainment_app' keys
            # Ensure they are lists and convert all keywords to lowercase for matching
            productive_keywords = [kw.lower() for kw in data.get('productivity_app', []) if isinstance(kw, str)]
            entertainment_keywords = [kw.lower() for kw in data.get('entertainment_app', []) if isinstance(kw, str)]

    except json.JSONDecodeError:
        print(f"Error: The categories file '{categories_file_path}' is not a valid JSON file. Attempting to re-create it.")
        _create_initial_json_file(categories_file_path) # Attempt to fix by re-creating
        # After re-creation, the keywords will be empty. We should then recursively call
        # the function to re-attempt classification with the now empty but valid file.
        # This will result in an "unclassified" message for the current app.
        return classify_app_or_website(app_name, categories_file_path)
    except Exception as e:
        return f"An unexpected error occurred while reading or processing '{categories_file_path}': {e}"

    # Convert the input app name to lowercase for case-insensitive matching
    app_name_lower = app_name.lower()

    # Check if the app name contains any productive keywords
    for keyword in productive_keywords:
        if keyword in app_name_lower:
            return f"'{app_name}' is a productive app/website."

    # Check if the app name contains any entertainment keywords
    for keyword in entertainment_keywords:
        if keyword in app_name_lower:
            return f"'{app_name}' is an entertainment app/website."

    # If no match is found in either category
    return f"'{app_name}' could not be classified. It's not listed in the provided categories."

# --- Example Usage ---
if __name__ == "__main__":
    print("--- App/Website Classifier ---")

    # Define the path to the categories file
    categories_file = "productivity.json"

    # Optional: Delete the file to test the creation functionality
    # if os.path.exists(categories_file):
    #     os.remove(categories_file)
    #     print(f"Deleted {categories_file} for testing purposes.")

    # Check and create the JSON file if it doesn't exist, *before* user input
    if not os.path.exists(categories_file):
        _create_initial_json_file(categories_file)
    # Also check if it's empty after existing, and re-initialize if so
    elif os.path.getsize(categories_file) == 0:
        print(f"Warning: '{categories_file}' is empty. Initializing its content.")
        _create_initial_json_file(categories_file)


    # Get the app/website name from the user
    user_input_app_name = input("Enter the app/website name (e.g., 'Netflix', 'Google Docs', 'Jira', 'VS Code'): ")

    # Classify the app/website
    classification_result = classify_app_or_website(user_input_app_name, categories_file)
    print(classification_result)

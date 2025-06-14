import os
import json

def _read_json_file(file_path):
    """
    Helper function to read JSON data from a file.
    Returns an empty dictionary if the file doesn't exist or is invalid.
    """
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: '{file_path}' is corrupted or empty. Starting with an empty JSON object.")
                return {}
            except Exception as e:
                print(f"Error reading '{file_path}': {e}. Starting with an empty JSON object.")
                return {}
    return {}

def _write_json_file(file_path, data):
    """
    Helper function to write JSON data to a file.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error: Could not write to '{file_path}'. Reason: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing to '{file_path}': {e}")


def save_points_to_json(points_value: int, file_path: str = "points.json"):
    """
    Saves or updates a 'points' value in a JSON file.
    If the file does not exist, it will be created.
    If the file exists but is empty or invalid JSON, it will be initialized.
    Points value must be a non-negative integer.

    Args:
        points_value (int): The integer value of points to save.
        file_path (str): The path to the JSON file where points will be stored.
                         Defaults to 'points.json'.
    """
    if not isinstance(points_value, int):
        print(f"Error: Points value must be an integer. Received: {type(points_value).__name__}")
        return

    # Ensure points_value is not negative
    if points_value < 0:
        print(f"Error: Points value cannot be negative. Received: {points_value}")
        return

    # Ensure the file exists and has a valid structure before attempting to read/write
    # This block will create the file if it's missing or re-initialize if empty/corrupted.
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        initial_data = {"points": 0} # Default initial points if file is new/empty
        _write_json_file(file_path, initial_data)
        print(f"Info: '{file_path}' not found or empty. Created/initialized with default points.")

    existing_data = _read_json_file(file_path)

    # Update the 'points' key in the dictionary
    existing_data['points'] = points_value

    # Write the updated dictionary back to the JSON file
    _write_json_file(file_path, existing_data)
    print(f"Points successfully saved to '{file_path}'. Current points: {points_value}")


def get_points_from_json(file_path: str = "points.json") -> int:
    """
    Retrieves the 'points' value from a JSON file.

    Args:
        file_path (str): The path to the JSON file. Defaults to 'points.json'.

    Returns:
        int: The points value, or 0 if the file/key is not found or invalid.
    """
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"Info: '{file_path}' not found or empty. Returning 0 points.")
        return 0

    data = _read_json_file(file_path)
    points = data.get('points', 0) # Get 'points' key, default to 0 if not found

    if not isinstance(points, int):
        print(f"Warning: 'points' value in '{file_path}' is not an integer. Returning 0.")
        return 0

    return points

# --- Add this block to your points.py file ---
if __name__ == "__main__":
    # This line will call save_points_to_json, which in turn
    # will create 'points.json' if it doesn't exist.
    # You can start with any non-negative number you like.
    save_points_to_json(0) # Initialize points to 0 on first run
    print(f"Program initialized. Current points: {get_points_from_json()}")

    # You can add more calls here if you want to test further, e.g.:
    # save_points_to_json(50)
    # print(f"Points after adding: {get_points_from_json()}")

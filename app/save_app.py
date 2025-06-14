import json
import os

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
                print(f"Warning: '{file_path}' is empty or corrupted. Starting with an empty JSON object.")
                return {}
    return {}

def _write_json_file(file_path, data):
    """
    Helper function to write JSON data to a file.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def _update_app_list(existing_data: dict, key: str, app_name: str) -> dict:
    """
    Helper function to update a list of apps under a given key in a dictionary.
    Ensures the key holds a list and prevents duplicates.
    """
    app_list = existing_data.get(key, [])

    # Ensure app_list is actually a list
    if not isinstance(app_list, list):
        if isinstance(app_list, str):
            app_list = [app_list]
        else:
            app_list = []
            print(f"Warning: '{key}' in data was not a list or string. Re-initializing.")

    # Add the new app_name if it's not already in the list
    if app_name not in app_list:
        app_list.append(app_name)
        print(f"'{app_name}' added to {key} list.")
    else:
        print(f"'{app_name}' is already in the {key} list. No new entry added.")

    existing_data[key] = app_list
    return existing_data

def save_app_to_productivity(app_name: str):
    """
    Adds an application name to a list under the 'productivity_app' key
    in 'productivity.json'. If the key does not exist or is not a list,
    it will be initialized/converted to a list.
    """
    file_path = "productivity.json"
    existing_data = _read_json_file(file_path)

    try:
        updated_data = _update_app_list(existing_data, 'productivity_app', app_name)
        _write_json_file(file_path, updated_data)
        print(f"Productivity apps successfully updated in '{file_path}'.")
    except IOError as e:
        print(f"Error saving data to file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def save_app_to_entertainment(app_name: str):
    """
    Adds an application name to a list under the 'entertainment_app' key
    in 'productivity.json'. If the key does not exist or is not a list,
    it will be initialized/converted to a list.
    """
    file_path = "productivity.json"
    existing_data = _read_json_file(file_path)

    try:
        updated_data = _update_app_list(existing_data, 'entertainment_app', app_name)
        _write_json_file(file_path, updated_data)
        print(f"Entertainment apps successfully updated in '{file_path}'.")
    except IOError as e:
        print(f"Error saving data to file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def remove_app_from_productivity(app_name: str):
    """
    Removes an application name from the 'productivity_app' list in 'productivity.json'.
    If the key does not exist or the app is not found, it will do nothing.
    """
    file_path = "productivity.json"
    existing_data = _read_json_file(file_path)

    if 'productivity_app' in existing_data:
        app_list = existing_data['productivity_app']
        if app_name in app_list:
            app_list.remove(app_name)
            existing_data['productivity_app'] = app_list
            _write_json_file(file_path, existing_data)
            print(f"'{app_name}' removed from productivity apps.")
        else:
            print(f"'{app_name}' not found in productivity apps.")
    else:
        print("No productivity apps found to remove.")

def remove_app_from_entertainment(app_name: str):
    """
    Removes an application name from the 'productivity_app' list in 'productivity.json'.
    If the key does not exist or the app is not found, it will do nothing.
    """
    file_path = "productivity.json"
    existing_data = _read_json_file(file_path)

    if 'entertainment_app' in existing_data:
        app_list = existing_data['entertainment_app']
        if app_name in app_list:
            app_list.remove(app_name)
            existing_data['entertainment_app'] = app_list
            _write_json_file(file_path, existing_data)
            print(f"'{app_name}' removed from entertainment apps.")
        else:
            print(f"'{app_name}' not found in entertainment apps.")
    else:
        print("No entertainment apps found to remove.")


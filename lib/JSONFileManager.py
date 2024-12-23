import os
import json
import logging
import glob


class JSONFileManager:

    def __init__(self, path) -> None:
        self.files = self._generate_file_list(path)
        self.json_data = {}

    def _generate_file_list(self, search_path: str) -> list:
        """
        Generate a list of JSON files based on the provided path.
        Handles directories, single files, and glob patterns.

        Returns:
            list: A list of file paths.
        """
        # Handle directory: return all JSON files in the directory
        if os.path.isdir(search_path):
            return [os.path.join(search_path, f) for f in os.listdir(search_path) if f.endswith('.json')]

        # Handle glob pattern: match all files specified by the pattern
        if '*' in search_path or '?' in search_path or '[' in search_path:
            matched_files = glob.glob(search_path)
            if matched_files:
                return matched_files
            else:
                logging.warning(f"No files matched glob pattern: {search_path}")
                return []

        # Handle single file: return if it is a valid JSON file
        if os.path.isfile(search_path):
            if search_path.endswith('.json'):
                return [search_path]
            else:
                logging.warning(f"Provided file is not a JSON file: {search_path}")
                return []

        # Invalid path
        logging.error(f"Invalid JSON path: {search_path}")
        return []

    def load_json_file(self, json_file):
        try:
            with open(json_file, 'r') as file:
                self.json_data = json.load(file)
        except Exception as e:
            logging.error(f"Failed to read file {json_file}: {e}")
            self.json_data = {}

        return self.json_data

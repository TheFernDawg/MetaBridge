import os
import logging
import shutil
import pytz
import time

from datetime import datetime
from lib.ExifImageHandler import ExifImageHandler  # Custom utility for handling EXIF metadata


# Set the timezone for timestamp formatting
la_timezone = pytz.timezone("America/Los_Angeles")


class MediaProcessor:
    def __init__(self, base_path: str, save_path: str, dry_run: bool = False):
        """
        Initializes the MediaProcessor class.

        Args:
            base_path (str): Base directory where source media files are located.
            save_path (str): Destination directory where processed media will be saved.
            dry_run (bool): If True, simulate operations without making actual changes.
        """
        self.base_path = base_path
        self.save_path = save_path
        self.metadata = {}
        self.is_dry_run = dry_run
        self.processed_items = set()  # (URI, save_directory) pairs

    def process_media_item(self, data: dict, save_directory: str) -> None:
        """
        Processes a single media item, determining its type and saving it accordingly.

        Args:
            data (dict): Metadata about the media item, including 'uri', 'description', and 'creation_timestamp'.
            save_directory (str): Target directory for the processed file.
        """
        uri = data.get('uri', '')

        # Skip Non-Local URIs
        if not uri.startswith("your_facebook_activity"):
            logging.debug(f"Skipped processing for irrelevant URI: {uri}")
            return

        # Create metadata object
        self.metadata = {
            "uri_path": os.path.join(self.base_path, uri),
            "description": data.get('description', ''),
            "creation_timestamp": data.get('creation_timestamp', int(time.time())),
            "taken_timestamp": self._extract_taken_timestamp(data),
            "save_directory": save_directory,
        }

        self.metadata["timestamp"] = self.metadata["taken_timestamp"] or self.metadata["creation_timestamp"]

        # Check if the (URI, save_directory) pair is already processed
        if (self.metadata["uri_path"], self.metadata["save_directory"]) in self.processed_items:
            logging.debug(f"Skipping already processed item: (URI: {uri}, Directory: {save_directory})")
            return

        # Determine file type and process accordingly
        file_extension = os.path.splitext(self.metadata["uri_path"])[1].lower()
        if file_extension in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}:
            self._copy_image()
        else:
            self._copy_non_image()

    def _copy_image(self) -> None:
        """
        Handles image files by updating their EXIF metadata and saving them.
        """
        # Determine file type and process accordingly
        if self.is_dry_run:
            logging.info(f"[Dry Run] Would process and save: {self.metadata['uri_path']}")
            return

        try:
            base_file_name = self._generate_filename()
            save_path = self._generate_save_path(self.metadata["save_directory"], base_file_name)

            if save_path is None:
                return

            exif_handler = ExifImageHandler(self.metadata["uri_path"])
            exif_handler.set_creation_timestamp(self.metadata["timestamp"])
            exif_handler.set_description(self.metadata["description"])
            exif_handler.save(save_path)

            logging.debug(f"Processed and saved image: {save_path}")
            self.processed_items.add((self.metadata["uri_path"], self.metadata["save_directory"]))

        except Exception as e:
            logging.error(f"Error processing image metadata for {self.metadata['uri_path']}: {e}")
            logging.warning(f"Copying image without metadata changes: {save_path}")
            self._copy_non_image()

    def _copy_non_image(self) -> None:
        """
        Processes non-image files by renaming and moving them to the target directory.
        """
        if self.is_dry_run:
            logging.info(f"[Dry Run] Would process and save: {self.metadata['uri_path']}")
            return

        try:
            base_file_name = self._generate_filename()
            save_path = self._generate_save_path(self.metadata["save_directory"], base_file_name)

            if save_path is None:
                return

            # Ensure the directory for the save path exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Copy the file
            shutil.copy(self.metadata["uri_path"], save_path)
            os.utime(save_path, (self.metadata["timestamp"], self.metadata["timestamp"]))

            logging.debug(f"Moved non-image file to: {save_path}")
            self.processed_items.add((self.metadata["uri_path"], self.metadata["save_directory"]))

        except Exception as e:
            logging.error(f"Error moving non-image file {self.metadata['uri_path']}: {e}")

    # Helper Methods
    def _generate_filename(self) -> str:
        """
        Creates a base file name based on the metadata's timestamp.

        Returns:
            str: A timestamp-based file name.
        """
        _, uri_file_name = os.path.split(self.metadata['uri_path'])
        _, file_ext = os.path.splitext(uri_file_name)
        file_dt = datetime.fromtimestamp(self.metadata['timestamp'], tz=la_timezone).strftime("%Y-%m-%d_%H.%M.%S")
        return f"{file_dt}{file_ext}"

    def _generate_save_path(self, directory: str, base_file_name: str) -> str:
        """
        Creates the final save path while resolving naming conflicts by appending a counter to the file name if needed.

        Args:
            directory (str): Directory where the file will be saved.
            base_file_name (str): Base file name.

        Returns:
            str: A unique file path with no conflicts.
        """
        file_name, file_ext = os.path.splitext(base_file_name)
        file_path = os.path.join(directory, base_file_name)
        counter = 1

        while os.path.exists(file_path):
            new_file_name = f"{file_name}_{counter}{file_ext}"
            file_path = os.path.join(directory, new_file_name)
            counter += 1

        if counter > 1:
            logging.debug(f"Resolved filename conflict: {file_path}")

        return file_path

    def _extract_taken_timestamp(self, media_item) -> int | None:
        """
        Extracts the 'taken_timestamp' from the media item's EXIF data, if available.

        Args:
            media_item (dict): Metadata about the media item.

        Returns:
            int | None: Extracted timestamp, or None if unavailable.
        """
        exif_data_list = media_item.get("media_metadata", {}).get("photo_metadata", {}).get("exif_data", [])
        for exif_data in exif_data_list:
            if "taken_timestamp" in exif_data:
                return exif_data["taken_timestamp"]
        return None

    def extract_attachment_data(self, entry):
        """
        Extracts media items from a post's attachments.

        Args:
            entry (dict): Post data containing potential attachments.

        Yields:
            dict: Media item data extracted from attachments.
        """
        for attachment in entry.get("attachments", []):
            if "data" in attachment:
                yield from attachment["data"]

    def get_total_processed(self) -> int:
        """
        Retrieves the total count of processed files.

        Returns:
            int: Total number of files processed.
        """
        return len(self.processed_items)

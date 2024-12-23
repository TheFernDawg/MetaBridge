import os
import logging
import time
import pytz

from datetime import datetime, timezone
from PIL import Image
from piexif import load, dump, ExifIFD, ImageIFD

la_timezone = pytz.timezone("America/Los_Angeles")


class ExifImageHandler:
    def __init__(self, photo_uri: str):
        self.photo_uri = photo_uri
        self.img, self.exif_dict = self._load_image_exif()
        logging.debug(f"Loaded {self.photo_uri}")

    def _load_image_exif(self) -> tuple[Image.Image, dict]:
        try:
            img = Image.open(self.photo_uri)
            exif_data = img.info.get("exif")
            exif_dict = load(exif_data) if exif_data else {"Exif": {}, "0th": {}, "1st": {}, "thumbnail": None}
            return img, exif_dict
        except FileNotFoundError:
            logging.error(f"File not found: {self.photo_uri}")
            raise
        except Exception as e:
            logging.error(f"Error loading EXIF data from {self.photo_uri}: {e}")
            raise

    def set_creation_timestamp(self, creation_timestamp: int) -> None:
        """
        Set the creation timestamp in EXIF metadata.

        Args:
            creation_timestamp (int): Unix timestamp for the creation time.
        """
        dt = datetime.fromtimestamp(creation_timestamp, tz=timezone.utc)
        exif_dt = dt.strftime("%Y:%m:%d %H:%M:%S")
        self.exif_dict['Exif'][ExifIFD.DateTimeOriginal] = exif_dt
        self.creation_timestamp = creation_timestamp
        logging.debug(f"Set creation timestamp to {exif_dt}")

    def set_description(self, description: str) -> None:
        """
        Set the image description in EXIF metadata.

        Args:
            description (str): Description for the image.
        """
        if description:
            self.exif_dict['0th'][ImageIFD.ImageDescription] = description
            logging.debug(f"Set description to \"{description}\"")

    def save(self, save_path: str) -> None:
        """
        Save the image with updated EXIF metadata to the specified path.

        Args:
            save_path (str): Full path (including file name) where the image will be saved.
        """
        # Render EXIF bytes
        exif_bytes = dump(self.exif_dict)

        # Ensure the directory for the save path exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Determine the format based on the file extension or the original image format
        _, file_ext = os.path.splitext(save_path)
        file_ext = file_ext.lower().replace(".", "")
        image_format = self.img.format if self.img.format else file_ext.upper()

        # Save the image with updated EXIF metadata
        self.img.save(save_path, format=image_format, exif=exif_bytes)
        logging.debug(f"Saved image in {image_format} format with updated EXIF: {save_path}")

        # Update the timestamps on the new file
        self.update_file_timestamps(save_path)

    def delete(self) -> None:
        if os.path.exists(self.photo_uri):
            try:
                os.remove(self.photo_uri)
                logging.debug(f"Old file removed: {self.photo_uri}")
            except Exception as e:
                logging.error(f"Error removing old file {self.photo_uri}: {e}")

    def get_all_exif_data(self) -> dict:
        """
        Retrieve all EXIF data in a readable format.

        Returns:
            dict: All EXIF data categorized by IFD sections.
        """
        all_exif = {}
        for ifd, tags in self.exif_dict.items():
            all_exif[ifd] = {}
            if tags:
                for tag, value in tags.items():
                    all_exif[ifd][tag] = value
        return all_exif

    def update_file_timestamps(self, image_path) -> None:
        """
        Update the file's creation and modification timestamps using the set creation timestamp.
        """

        timestamp = getattr(self, 'creation_timestamp', time.time())

        os.utime(image_path, (timestamp, timestamp))
        logging.debug(f"Updated file timestamps for: {image_path}")

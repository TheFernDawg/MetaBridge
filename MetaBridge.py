import os
import logging
import argparse
import pytz

from lib.JSONFileManager import JSONFileManager
from lib.MediaProcessor import MediaProcessor

la_timezone = pytz.timezone("America/Los_Angeles")

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set the minimum logging level for the logger

# Create a file handler for DEBUG level and above
file_handler = logging.FileHandler("results.log", mode="w")
file_handler.setLevel(logging.DEBUG)  # Log DEBUG and higher levels to the file
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Create a console handler for INFO level and above
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Log INFO and higher levels to the console
console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


# Global MediaProcessor
media_processor = None


def extract_albums() -> int:
    # Load all the JSON files for this section
    target_path = os.path.join(args.path, 'your_facebook_activity/posts/album/*.json')
    file_manager = JSONFileManager(target_path)
    json_header_key = "photos"

    # Keep Count of count differences
    starting_count = media_processor.get_total_processed()

    # Parse Through the JSON Files
    for json_file in file_manager.files:
        data = file_manager.load_json_file(json_file)

        # Get Album Meta Data
        album_name = data.get('name', '')
        save_directory = os.path.join(args.save_path, 'albums', album_name)

        # Process each media item
        for media_item in data.get(json_header_key, []):
            media_processor.process_media_item(media_item, save_directory)

    processed_count = media_processor.get_total_processed() - starting_count
    logging.info(f"Processed {processed_count} Album Media Items {os.path.join(args.save_path, 'albums')}")


def extract_posts() -> int:
    # Load all the JSON files for this section
    target_path = os.path.join(
        args.path, 'your_facebook_activity/posts/your_posts__check_ins__photos_and_videos*.json')
    file_manager = JSONFileManager(target_path)
    save_directory = os.path.join(args.save_path, 'posts')

    # Keep Count of count differences
    starting_count = media_processor.get_total_processed()

    # Parse Through the JSON Files
    for json_file in file_manager.files:
        data = file_manager.load_json_file(json_file)

        # Extract and process media items from posts
        for post in data:
            for attachment_data in media_processor.extract_attachment_data(post):
                if 'media' in attachment_data:
                    media_processor.process_media_item(attachment_data['media'], save_directory)

    processed_count = media_processor.get_total_processed() - starting_count
    logging.info(f"Processed {processed_count} Post Media Items in {save_directory}.")


def extract_misc() -> int:
    # Define file paths and header key
    target_path = os.path.join(args.path, 'your_facebook_activity/posts/your_uncategorized_photos*.json')
    save_directory = os.path.join(args.save_path, 'uncategorized_photos')
    json_header_key = "other_photos_v2"

    # Keep Count of count differences
    starting_count = media_processor.get_total_processed()

    # Load JSON files
    file_manager = JSONFileManager(target_path)

    # Parse and process each file
    for json_file in file_manager.files:
        data = file_manager.load_json_file(json_file)
        for entry in data.get(json_header_key, []):
            media_processor.process_media_item(entry, save_directory)

    processed_count = media_processor.get_total_processed() - starting_count
    logging.info(f"Processed {processed_count} Misc Media Items in {save_directory}.")


def extract_videos() -> int:
    # Define file paths and header key
    target_path = os.path.join(args.path, 'your_facebook_activity/posts/your_videos*.json')
    save_directory = os.path.join(args.save_path, 'videos')
    json_header_key = "videos_v2"

    # Keep Count of count differences
    starting_count = media_processor.get_total_processed()

    # Load JSON files
    file_manager = JSONFileManager(target_path)

    # Parse Through the JSON Files
    for json_file in file_manager.files:
        data = file_manager.load_json_file(json_file)

        for entry in data.get(json_header_key, []):
            media_processor.process_media_item(entry, save_directory)

    processed_count = media_processor.get_total_processed() - starting_count
    logging.info(f"Processed {processed_count} Video Media Items in {save_directory}.")


def extract_stories() -> int:
    # Define file paths and header key
    target_path = os.path.join(args.path, 'your_facebook_activity/stories/archived_stories*.json')
    save_directory = os.path.join(args.save_path, 'stories')
    json_header_key = "archived_stories_v2"

    # Keep Count of count differences
    starting_count = media_processor.get_total_processed()

    # Load JSON files
    file_manager = JSONFileManager(target_path)

    # Parse Through the JSON Files
    for json_file in file_manager.files:
        data = file_manager.load_json_file(json_file)
        for entry in data.get(json_header_key, []):
            for attachment_data in media_processor.extract_attachment_data(entry):
                if 'media' in attachment_data:
                    media_processor.process_media_item(attachment_data['media'], save_directory)

    processed_count = media_processor.get_total_processed() - starting_count
    logging.info(f"Processed {processed_count} Story Media Items in {save_directory}.")


def process_reels() -> int:
    # Define file paths and header key
    target_path = os.path.join(args.path, 'your_facebook_activity/short_videos/your_reels*.json')
    save_directory = os.path.join(args.save_path, 'reels')
    json_header_key = "lasso_videos_v2"

    # Keep Count of count differences
    starting_count = media_processor.get_total_processed()

    # Load JSON files
    file_manager = JSONFileManager(target_path)

    # Parse Through the JSON Files
    for json_file in file_manager.files:
        data = file_manager.load_json_file(json_file)

        for entry in data.get(json_header_key, []):
            for attachment_data in media_processor.extract_attachment_data(entry):
                if 'media' in attachment_data:
                    media_processor.process_media_item(attachment_data['media'], save_directory)

    processed_count = media_processor.get_total_processed() - starting_count
    logging.info(f"Processed {processed_count} Reel Media Items in {save_directory}.")


def process_stickers():
    uri_base = 'your_facebook_activity/posts/media/stickers_used/'
    target_path = os.path.join(args.path, uri_base)
    save_directory = os.path.join(args.save_path, 'stickers')

    # Keep Count of count differences
    starting_count = media_processor.get_total_processed()

    # Check if there is a sticker path.
    if not os.path.exists(target_path) or not os.path.isdir(target_path):
        logging.warning(f"Stickers directory does not exist or is not a directory: {target_path}")
        return 0

    # Manually Create Sticker Metadata and process them.
    for file_name in os.listdir(target_path):
        file_path = os.path.join(target_path, file_name)

        if os.path.isfile(file_path):
            try:
                # Process the sticker file as a non-image item
                data = {
                    "uri": os.path.join(uri_base, file_name),
                    "description": "",
                    "creation_timestamp": int(os.path.getctime(file_path)),  # Use file creation time
                }
                media_processor.process_media_item(data, save_directory)
            except Exception as e:
                logging.error(f"Failed to process sticker file: {file_path}. Error: {e}")

    processed_count = media_processor.get_total_processed() - starting_count
    logging.info(f"Processed {processed_count} Sticker Media Items in {save_directory}.")


def main() -> None:

    logging.info(f"Starting Processing in {args.path}.")

    extract_posts()
    extract_albums()
    extract_misc()
    extract_videos()
    extract_stories()
    process_reels()
    process_stickers()

    logging.info(f"Done! Processed {media_processor.get_total_processed()} files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MetaBridge EXIF Metadata Processor.")
    parser.add_argument("path", type=str, help="Path to the `your_facebook_activity` directory")
    parser.add_argument("-d", "--save-path", type=str, default="./processed/",
                        help="Directory to save processed files (default: ./processed/)")
    parser.add_argument("--dry-run", action="store_true", help="Run without making changes")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    # Initialize MediaProcessor
    media_processor = MediaProcessor(args.path, args.save_path, args.dry_run)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.dry_run:
        logging.info("[Dry Run] Dry run mode enabled; no changes will be made.")

    main()

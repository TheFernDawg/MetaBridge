# MetaBridge

**Author:** Fernando Vasquez, @theferndawg

## Overview

This project processes Facebook activity JSON files extracted from the Facebook Download Your Information tool. Media files exported by Facebook, such as photos and videos, often lack proper metadata (e.g., accurate timestamps, descriptions, and contextual details). Instead, this crucial information is stored separately in JSON files.

The application bridges this gap by extracting metadata from the JSON files and embedding it directly into the media files, ensuring that timestamps, descriptions, and other details are preserved in a standard format. It specializes in managing EXIF metadata for images and organizes different types of media into logical categories, including albums, posts, videos, and stories. This approach simplifies archiving and enhances compatibility with various media management tools.

## Features

- **JSON Parsing**: Reads Facebook activity data from JSON files.
- **Media Processing**: Processes and organizes images, videos, and other media files.
- **EXIF Metadata Management**: Extracts and updates EXIF metadata for images.
- **Dry-Run Mode**: Simulates operations without making actual changes.

## Project Structure

```
project/
├── MetaBridge.py              # Entry point for the application
├── lib/
│   ├── ExifImageHandler.py    # Utility for handling EXIF metadata
│   ├── MediaProcessor.py      # Main class for processing media files
│   ├── JSONFileManager.py     # Utility for managing JSON files
```

## Requirements

- Python 3.8 or higher
- Dependencies:
  - `pytz`
  - `Pillow`
  - `piexif`

Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage

### Command-Line Interface

The script is run via the command line and accepts several arguments:

```bash
python MetaBridge.py PATH [-d SAVE_PATH] [--dry-run] [--verbose]
```

- `PATH`: Path to the `your_facebook_activity` directory.
- `-d, --save-path`: Directory to save processed files (default: `./processed/`).
- `--dry-run`: Enables dry-run mode to simulate operations.
- `--verbose`: Enables verbose logging.

### Example

```bash
python MetaBridge.py /path/to/facebook_activity -d /path/to/output --verbose
```

### Processing Media Types

The script processes various Facebook media types:

1. **Albums**: Extracts photos from albums.
2. **Posts**: Extracts photos and videos from posts.
3. **Miscellaneous Media**: Processes uncategorized photos.
4. **Videos**: Organizes video files.
5. **Stories**: Handles archived stories.
6. **Reels**: Processes short videos (Reels).
7. **Stickers**: Organizes stickers into the output directory.

## Dry-Run Mode

Use the `--dry-run` option to simulate the processing without modifying files. This is useful for verifying the operation before execution.

## Contributing

Contributions are welcome! Please ensure your code is well-documented and follows the project's coding standards.

## License
This project is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).

You are free to:
- Share: Copy and redistribute the material in any medium or format.
- Adapt: Remix, transform, and build upon the material.

**Under the following terms:**
- **Attribution**: You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **NonCommercial**: You may not use the material for commercial purposes.
- **ShareAlike**: If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

For more details, see the [full license](https://creativecommons.org/licenses/by-nc-sa/4.0/).
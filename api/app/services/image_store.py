import json
import os
from pathlib import Path
from typing import List, Optional, Dict

class ImageStore:
    def __init__(self, base_dir: str = "ai-assistant/api"):
        self.base_dir = Path(base_dir)
        self.uploads_dir = self.base_dir / "uploads"
        self.metadata_file = self.base_dir / "metadata.json"

        # Ensure uploads directory exists
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

        # Initialize metadata file if it doesn't exist
        if not self.metadata_file.exists():
            self._save_metadata({"avatar": None, "gallery": []})

    def _load_metadata(self) -> Dict:
        try:
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"avatar": None, "gallery": []}

    def _save_metadata(self, data: Dict):
        with open(self.metadata_file, "w") as f:
            json.dump(data, f, indent=4)

    def get_all(self) -> Dict:
        return self._load_metadata()

    def save_image(self, filename: str, content: bytes) -> str:
        file_path = self.uploads_dir / filename
        with open(file_path, "wb") as f:
            f.write(content)

        metadata = self._load_metadata()
        if filename not in metadata["gallery"]:
            metadata["gallery"].append(filename)
        self._save_metadata(metadata)

        return str(file_path)

    def set_avatar(self, filename: str):
        metadata = self._load_metadata()
        if filename not in metadata["gallery"]:
            raise FileNotFoundError(f"Image {filename} not found in gallery")
        metadata["avatar"] = filename
        self._save_metadata(metadata)

    def delete_image(self, filename: str):
        # Remove from disk
        file_path = self.uploads_dir / filename
        if file_path.exists():
            os.remove(file_path)

        # Remove from metadata
        metadata = self._load_metadata()
        if filename in metadata["gallery"]:
            metadata["gallery"].remove(filename)
        if metadata["avatar"] == filename:
            metadata["avatar"] = None
        self._save_metadata(metadata)

image_store = ImageStore()

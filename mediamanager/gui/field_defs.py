"""Shared field definitions for metadata editors."""

from __future__ import annotations

# Fields shown in the GUI write section, grouped by category
ALL_FIELD_GROUPS: list[tuple[str, list[str]]] = [
    ("Basic", ["title", "artist", "copyright", "description", "comment"]),
    ("Camera & Lens", ["make", "model", "lens_make", "lens_model"]),
    ("Date / Time", ["datetime", "datetime_original", "datetime_digitized"]),
    ("Other", ["software", "keywords", "subject", "orientation", "iso"]),
    ("GPS (decimal degrees)", ["gps_latitude", "gps_longitude"]),
]

FIELD_LABELS: dict[str, str] = {
    "title": "Title",
    "artist": "Artist",
    "copyright": "Copyright",
    "description": "Description",
    "comment": "Comment",
    "make": "Camera Make",
    "model": "Camera Model",
    "lens_make": "Lens Make",
    "lens_model": "Lens Model",
    "datetime": "Date/Time",
    "datetime_original": "Date Original",
    "datetime_digitized": "Date Digitized",
    "software": "Software",
    "keywords": "Keywords",
    "subject": "Subject",
    "orientation": "Orientation",
    "iso": "ISO",
    "gps_latitude": "GPS Latitude",
    "gps_longitude": "GPS Longitude",
}

FIELD_PLACEHOLDERS: dict[str, str] = {
    "datetime": "YYYY:MM:DD HH:MM:SS",
    "datetime_original": "YYYY:MM:DD HH:MM:SS",
    "datetime_digitized": "YYYY:MM:DD HH:MM:SS",
    "keywords": "keyword1; keyword2; ...",
    "orientation": "1-8",
    "iso": "100-65535",
    "gps_latitude": "e.g. 40.7128",
    "gps_longitude": "e.g. -74.0060",
}

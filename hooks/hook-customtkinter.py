"""PyInstaller hook for customtkinter — ensures theme/assets are bundled."""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("customtkinter")

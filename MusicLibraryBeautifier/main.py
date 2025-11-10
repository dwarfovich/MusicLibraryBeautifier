import sys
import mimetypes
import shutil
import os
import re
import uuid
from pathlib import Path

_m3u_regex = r"(?i)\.m3u8?$"
_audio_extensions_not_in_mime = [".ape", ".wv", ".ac3", ".caf", ".m4b", ".tta", ".voc", ".wma"]
_cue_extension = ".cue"
_log_extension = ".log"
_temp_folder_suffix = "as140izeowq34"
_maximum_item_suffix = 100

def is_audio_file(path: Path):
     mime, _ = mimetypes.guess_type(path)
     m3u_pattern = re.compile(_m3u_regex)
     if mime and mime.startswith("audio/") and not m3u_pattern.search(path.name):
         return True
     return path.suffix in _audio_extensions_not_in_mime

def is_image_file(path: Path):
    mime, _ = mimetypes.guess_type(path)
    return mime is not None and mime.startswith("image/")

def is_cue_file(path: Path):
    return (path.suffix == ".cue")

def is_log_file(path: Path):
    return (path.suffix == ".log")

def is_audio_image_file(path: Path):
    parent = path.parent
    filename, _ = os.path.splitext(path)
    if is_audio_file(path):
        return (parent / (filename + _cue_extension)).exists() or (parent / (filename + _log_extension)).exists()
    extension = path.suffix
    if extension == _cue_extension:
        for item in parent.glob("*"):
            item_filename, _ = os.path.splitext(item)
            if item_filename == filename and is_audio_file(item):
                return True
    if extension == _log_extension:
        for item in parent.glob("*"):
            item_filename, _ = os.path.splitext(item)
            if item_filename == filename and is_audio_file(item):
                return True
    return False

def is_misc_file(path: Path, is_audio_image_album: bool):
    if is_audio_image_album:
        return not is_audio_file(path)
    else:
        return not is_audio_image_file(path)

def is_deepest_audio_folder(path: Path):
    if path.is_file():
        return False
    
    has_audio_file = False
    for item in path.rglob("*"):
        if item.is_file():
            if item.parent == path:
                if not has_audio_file and is_audio_file(item):
                    has_audio_file = True
            elif is_audio_file(item):
                return False

    return has_audio_file

def base_name(path: Path):
    return re.sub(r'(\.[^.]+)+$', '', path.name)

def ensure_folder_exists(path: Path):
    if not path.exists():
        path.mkdir(parents = True, exist_ok = True)

def ensure_folder_uppercased(path: Path):
    if not path.exists():
        raise RuntimeError("The path doesn't exist")
    parent_dir = os.path.dirname(path)
    current_folder_name = os.path.basename(path)
    temp_path = Path(parent_dir) / (current_folder_name + _temp_folder_suffix)
    os.rename(path, temp_path)
    new_folder_name = current_folder_name.capitalize()
    os.rename(temp_path, Path(parent_dir) / new_folder_name)

def move_and_rename_if_exists(source_path: Path, target_folder_path: Path):
    name = source_path.name
    new_path = Path()
    if (target_folder_path / name).exists():
        index = 1
        base_filename = base_name(source_path)
        while True:
            new_name = base_filename + " (" + str(index) + ")" + source_path.suffix
            new_path = target_folder_path / new_name
            if not new_path.exists():
                break
            else:
                ++index
                if index > _maximum_item_suffix:
                    new_path = target_folder_path / uuid.uuid4()
                    break;
    else:
        new_path = target_folder_path / name

    target_folder_path.mkdir(parents = True, exist_ok = True)
    shutil.move(source_path, new_path)

def move_files_into_folder(source_path: Path, target_path: Path, filter):
    for item in source_path.rglob("*"):
        if target_path in item.parents:
            continue
        if item.is_file() and filter(item):
            move_and_rename_if_exists(item, target_path)

def move_misc_files_into_folder(source_path: Path, target_path: Path):
    for item in source_path.glob("*"):
        if (target_path in item.parents) or (item == target_path):
            continue
        if item.is_file():
            if not is_audio_image_file(item) and not is_audio_file(item) and not is_image_file(item):
                move_and_rename_if_exists(item, target_path)
        elif (item.name != Names.artwork_folder_name()):
            shutil.move(item, target_path / item.name)

def beautify_artwork(album_path: Path):
    artwork_folder_path = (album_path / Names.artwork_folder_name()).absolute()
    ensure_folder_exists(artwork_folder_path)
    ensure_folder_uppercased(artwork_folder_path)
    move_files_into_folder(album_path, artwork_folder_path, is_image_file)

def beautify_misc(album_path: Path):
    misc_folder_path = (album_path / Names.misc_folder_name()).absolute()
    ensure_folder_exists(misc_folder_path)
    ensure_folder_uppercased(misc_folder_path)
    move_misc_files_into_folder(album_path, misc_folder_path)

def remove_folders_wo_files_recursively(album_path: Path):
    for folder in sorted(album_path.rglob("*"), reverse = True):
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()

def remove_files(album_path: Path, regex: str):
    pattern = re.compile(regex)
    for file in album_path.rglob("*"):
        if file.is_file() and pattern.search(file.name):
            file.unlink()

def beautify_album_folder(path):
    print("Beautifying: " + str(path))
    beautify_artwork(path)
    beautify_misc(path)
    remove_files(path, _m3u_regex)
    remove_folders_wo_files_recursively(path)

class Names:
    @staticmethod
    def artwork_folder_name():
        return "Artwork"
    @staticmethod
    def misc_folder_name():
        return "Misc"
    @staticmethod
    def cd_number_folder(number):
        return "CD " + number

def main():
    path = Path(r"D:\Music")
    #path = Path(r"C:\Users\Boo\Desktop\TestMusic")
    #path = Path(r"C:\Boo\Temp\TestMusic")
    for item in path.rglob("*"):
        if is_deepest_audio_folder(item):
            beautify_album_folder(item)

if __name__ == "__main__":
    main()
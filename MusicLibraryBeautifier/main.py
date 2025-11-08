from genericpath import isdir
import sys
import mimetypes
import shutil
import os
from pathlib import Path
from xmlrpc.client import boolean

_audio_extensions_not_in_mime = [".ape", ".wv", ".ac3", ".caf", ".m4b", ".tta", ".voc", ".wma"]

def is_audio_file(path: Path):
     mime, _ = mimetypes.guess_type(path)
     if mime and mime.startswith("audio/"):
         return True
     return path.suffix in _audio_extensions_not_in_mime

def is_image_file(path: Path):
    mime, _ = mimetypes.guess_type(path)
    return mime is not None and mime.startswith("image/")

def is_cue_file(path: Path):
    return (path.suffix == ".cue") or (path.suffix == ".cue-original")

def is_log_file(path: Path):
    return (path.suffix == ".log")

def is_audio_image_file(path: Path):
    parent = path.parent
    filename, _ = os.path.splitext(path)
    if is_audio_file(path):
        return (parent / (filename + ".cue")).exists() or (parent / (filename + ".log")).exists()
    extension = path.suffix
    if extension == ".cue":
        for item in parent.glob("*"):
            item_filename, _ = os.path.splitext(item)
            if item_filename == filename and is_audio_file(item):
                return True
    if extension == ".log":
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


# def is_album_folder(path: Path):
#     for item in path.glob("*"):
#         if item.is_dir():
#             continue
#         if is_audio_file(item):
#             return True
        
#     return False

def ensure_folder_exists(path: Path):
    if not path.exists():
        path.mkdir(parents = True, exist_ok = True)

def ensure_folder_uppercased(path: Path):
    parent_dir = os.path.dirname(path)
    current_folder_name = os.path.basename(path)
    new_folder_name = current_folder_name.title()
    if current_folder_name is not new_folder_name:
         os.rename(path, Path(parent_dir) / new_folder_name)

def move_files_into_folder(source_path: Path, target_path: Path, filter):
    for item in source_path.rglob("*"):
        if target_path in item.parents:
            continue
        if item.is_file() and filter(item):
            shutil.move(item, target_path / item.name)

def move_misc_files_into_folder(source_path: Path, target_path: Path):
    for item in source_path.glob("*"):
        if target_path in item.parents or item == target_path or item.name == Names.artwork_folder_name():
            continue
        if item.is_file():
            if not is_audio_image_file(item) and not is_audio_file(item) and not is_image_file(item):
                shutil.move(item, target_path / item.name)
        else:
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
    for folder in sorted(album_path.rglob("*"), reverse=True):
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()

def beautify_album_folder(path):
    print("Beautifying: " + str(path))
    beautify_artwork(path)
    beautify_misc(path)
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
    print(os.getcwd())
    print("Hello")
    # root = Path("TestMusic")

    # shutil.rmtree(root, True)
    # destination = Path(".") / "TestMusic" # copy into current folder as "TestMusic"
    # shutil.copytree(Path("C:\\Users\\Boo\\Desktop\\TestMusic"), destination, dirs_exist_ok=True)
    # for item in root.rglob("*"):
    #     if is_album_folder(item):
    #         beautify_album_folder(item)

    #root = Path("Test").absolute()
    #print(str(root))
    #print(root.exists());
    #root.rename("Test") # in case it is lowercased
    #print(root.exists());
    #file = Path("Test2/t.txt")
    #shutil.move(file, "Test")

if __name__ == "__main__":
    main()
from pathlib import Path
from pyfakefs.fake_filesystem_unittest import TestCase

from main import ensure_folder_exists, is_audio_image_file
from main import ensure_folder_uppercased
from main import move_files_into_folder
from main import is_image_file
from main import is_audio_image_file

class FakeFileSystemTests(TestCase):
    def setUp(self):
        self.setUpPyfakefs()

def test_ensure_folder_exists_creation(fs):
    path = Path("/root")
    assert not path.exists()
    ensure_folder_exists(path)
    assert path.exists()
    assert path.is_dir()

    path = Path("/root/folder1/folder2")
    assert not path.exists()
    ensure_folder_exists(path)
    assert path.exists()
    assert path.is_dir()

def test_ensure_folder_uppercased(fs):
    cased_folder = "Folder"
    path = Path("/root") / "folder"
    fs.create_dir(path)
    ensure_folder_uppercased(path)
    assert(cased_folder in [entry.name for entry in Path("/root").iterdir()])

    cased_folder = "Folder2"
    path = Path("/Root") / cased_folder
    fs.create_dir(path)
    ensure_folder_uppercased(path)
    assert(cased_folder in [entry.name for entry in Path("/root").iterdir()])

def test_move_files_into_folder(fs):
    source_path = Path("/root/folder")
    fs.create_dir(source_path)
    images = ["image0.png", "image1.jpg", "image2.jpeg", "image3.png", "image4.png"]
    fs.create_file(source_path / images[0])
    fs.create_file(source_path / images[1])
    fs.create_file(source_path / images[2])
    fs.create_file(source_path / "artwork" / images[3])
    fs.create_file(source_path / "misc" / images[4])
    misc_files = ["text.txt", "log.log", "cue.cue"]
    fs.create_file(source_path / misc_files[0])
    fs.create_file(source_path / "artwork" / misc_files[1])
    fs.create_file(source_path / "misc" / misc_files[2])

    artwork_folder_path = source_path / "Artwork"
    move_files_into_folder(source_path, artwork_folder_path, is_image_file)
    
    for image in images:
        assert(artwork_folder_path / image).exists()
    assert((source_path / misc_files[0]).exists())
    assert((source_path / "artwork" / misc_files[1]).exists())
    assert((source_path / "misc" / misc_files[2]).exists())

def test_is_audio_image_file_sanity(fs):
    source_path = Path("/root/folder")
    fs.create_file(source_path / "album.mp3")
    fs.create_file(source_path / "album.cue")
    fs.create_file(source_path / "album.log")
    assert(is_audio_image_file(source_path / "album.mp3"))
    assert(is_audio_image_file(source_path / "album.cue"))
    assert(is_audio_image_file(source_path / "album.log"))
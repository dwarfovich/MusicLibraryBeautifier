from pathlib import Path
from pyfakefs.fake_filesystem_unittest import TestCase

from main import ensure_folder_exists, is_audio_image_file
from main import ensure_folder_uppercased
from main import move_files_into_folder
from main import is_image_file
from main import is_audio_image_file
from main import move_misc_files_into_folder
from main import is_audio_file
from main import remove_folders_wo_files_recursively

class FakeFileSystemTests(TestCase):
    def setUp(self):
        self.setUpPyfakefs()

def test_is_audio_file(fs):
    assert(is_audio_file(Path("track.mp3")))
    assert(is_audio_file(Path("track.flac")))
    assert(is_audio_file(Path("track.ape")))
    assert(is_audio_file(Path("track.ogg")))
    assert(is_audio_file(Path("track.wv")))
    assert(is_audio_file(Path("track.ac3")))
    assert(is_audio_file(Path("track.caf")))
    assert(is_audio_file(Path("track.m4b")))
    assert(is_audio_file(Path("track.tta")))
    assert(is_audio_file(Path("track.voc")))
    assert(is_audio_file(Path("track.wma")))

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
    fs.create_file(source_path / "album.txt")
    assert(is_audio_image_file(source_path / "album.mp3"))
    assert(is_audio_image_file(source_path / "album.cue"))
    assert(is_audio_image_file(source_path / "album.log"))
    assert(not is_audio_image_file(source_path / "album.txt"))

def test_is_audio_image_file_sanity_2(fs):
    source_path = Path("/root/folder")
    fs.create_file(source_path / "album.flac")
    fs.create_file(source_path / "album.cue")
    fs.create_file(source_path / "album.log")
    fs.create_file(source_path / "album.txt")
    fs.create_file(source_path / "album2.flac")
    fs.create_file(source_path / "album2.cue")
    fs.create_file(source_path / "album2.txt")
    assert(is_audio_image_file(source_path / "album.flac"))
    assert(is_audio_image_file(source_path / "album.cue"))
    assert(is_audio_image_file(source_path / "album.log"))
    assert(not is_audio_image_file(source_path / "album.txt"))
    assert(is_audio_image_file(source_path / "album2.flac"))
    assert(is_audio_image_file(source_path / "album2.cue"))
    assert(not is_audio_image_file(source_path / "album2.txt"))

def test_is_not_audio_image_file(fs):
    source_path = Path("/root/folder")
    fs.create_file(source_path / "track1.flac")
    fs.create_file(source_path / "track2.flac")
    fs.create_file(source_path / "track3.flac")
    fs.create_file(source_path / "track1.txt")
    assert(not is_audio_image_file(source_path / "track1.flac"))
    assert(not is_audio_image_file(source_path / "track2.flac"))
    assert(not is_audio_image_file(source_path / "track3.flac"))
    assert(not is_audio_image_file(source_path / "track1.txt"))

def test_is_not_audio_image_file_single_file(fs):
    source_path = Path("/root/folder")
    fs.create_file(source_path / "track1.flac")
    assert(not is_audio_image_file(source_path / "track1.flac"))

def test_move_misc_files_into_folder(fs):
    source_path = Path("/root/album")
    misc_path = source_path / "Misc"
    ensure_folder_exists(misc_path)
    fs.create_file(source_path / "album.wv")
    fs.create_file(source_path / "album.cue")
    fs.create_file(source_path / "album.log")
    fs.create_file(source_path / "album.txt")
    fs.create_file(source_path / "album.accurip")
    fs.create_file(source_path / ".accurip")
    fs.create_file(source_path / "image.png")
    fs.create_file(source_path / "file")
    move_misc_files_into_folder(source_path, misc_path)
    assert((source_path / "album.wv").exists())
    assert((source_path / "album.cue").exists())
    assert((source_path / "album.log").exists())
    assert((source_path / "image.png").exists())
    assert((misc_path / "album.txt").exists())
    assert((misc_path / "album.accurip").exists())
    assert((misc_path / ".accurip").exists())
    assert((misc_path / "file").exists())
    assert(not (source_path / "album.txt").exists())
    assert(not (source_path / "album.accurip").exists())
    assert(not (source_path / ".accurip").exists())
    assert(not (source_path / "file").exists())

def test_not_move_misc_files_into_folder(fs):
    source_path = Path("/root/album")
    misc_path = source_path / "Misc"
    ensure_folder_exists(misc_path)
    fs.create_file(source_path / "track1.ape")
    fs.create_file(source_path / "track1.log")
    fs.create_file(source_path / "track1.cue")
    fs.create_file(source_path / "track2.ape")
    fs.create_file(source_path / "track3.ape")
    fs.create_file(source_path / "track4.ape")
    move_misc_files_into_folder(source_path, misc_path)
    assert((source_path / "track1.ape").exists())
    assert((source_path / "track1.log").exists())
    assert((source_path / "track1.cue").exists())
    assert((source_path / "track2.ape").exists())
    assert((source_path / "track3.ape").exists())
    assert((source_path / "track4.ape").exists())
    assert(not any(misc_path.iterdir()))

def test_move_misc_files_into_folder_not_image(fs):
    source_path = Path("/root/album")
    misc_path = source_path / "Misc"
    ensure_folder_exists(misc_path)
    fs.create_file(source_path / "track1.ape")
    fs.create_file(source_path / "a.log")
    fs.create_file(source_path / "b.cue")
    fs.create_file(source_path / "track2.ape")
    fs.create_file(source_path / "track3.ape")
    fs.create_file(source_path / "track4.ape")
    move_misc_files_into_folder(source_path, misc_path)
    assert((source_path / "track1.ape").exists())
    assert((source_path / "track2.ape").exists())
    assert((source_path / "track3.ape").exists())
    assert((source_path / "track4.ape").exists())
    assert(not (source_path / "a.log").exists())
    assert(not (source_path / "b.cue").exists())
    assert((misc_path / "a.log").exists())
    assert((misc_path / "b.cue").exists())

def test_remove_folders_wo_files_recursively(fs):
    source_path = Path("/root/album")
    fs.create_dir(source_path / "f1")
    fs.create_dir(source_path / "f2/f3")
    fs.create_file(source_path / "f4/q.txt")
    fs.create_file(source_path / "f5/f6/q.txt")
    remove_folders_wo_files_recursively(source_path)
    assert(not (source_path / "f1").exists())
    assert(not (source_path / "f2").exists())
    assert((source_path / "f4/q.txt").exists())
    assert((source_path / "f5/f6/q.txt").exists())
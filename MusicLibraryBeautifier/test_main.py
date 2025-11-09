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
from main import remove_files
from main import _m3u_regex
from main import beautify_album_folder
from main import move_and_rename_if_exists

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

    cased_folder = "Folder3"
    path = Path("C:/Root") / "folder3"
    fs.create_dir(path)
    ensure_folder_uppercased(path)
    assert(cased_folder in [entry.name for entry in Path("C:/root").iterdir()])

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

def test_remove_files(fs):
    source_path = Path("/root/album")
    fs.create_file(source_path / "f1")
    fs.create_file(source_path / "f2.")
    fs.create_file(source_path / "f3.m3u")
    fs.create_file(source_path / ".m3u")
    fs.create_file(source_path / ".m3u8")
    fs.create_file(source_path / "f4.m3u8")
    fs.create_file(source_path / "m3u" / "f5.m3u8")
    fs.create_file(source_path / "f6.m3")
    fs.create_file(source_path / "f7.m3uq")
    remove_files(source_path, _m3u_regex)
    assert((source_path / "f1").exists())
    assert((source_path / "f2.").exists())
    assert((source_path / "f6.m3").exists())
    assert((source_path / "m3u").exists())
    assert((source_path / "f7.m3uq").exists())
    assert(not (source_path / "f3.m3u").exists())
    assert(not (source_path / ".m3u").exists())
    assert(not (source_path / ".m3u8").exists())
    assert(not (source_path / "f4.m3u8").exists())
    assert(not (source_path / "m3u" / "f5.m3u8").exists())

def test_move_and_rename_if_exists_file_not_exists(fs):
    source_path = Path(r"C:\t.txt")
    fs.create_file(source_path)
    target_folder_path = Path(r"C:\folder")
    move_and_rename_if_exists(source_path, target_folder_path)
    assert((target_folder_path / "t.txt").exists())
    assert(not source_path.exists())

def test_move_and_rename_if_exists_file_exists(fs):
    source_path = Path(r"C:\t.txt")
    fs.create_file(source_path)
    target_folder_path = Path(r"C:\folder")
    fs.create_file(target_folder_path / source_path.name)
    move_and_rename_if_exists(source_path, target_folder_path)
    assert((target_folder_path / "t.txt").exists())
    assert((target_folder_path / "t (1).txt").exists())
    assert(not source_path.exists())

def test_move_and_rename_if_exists_folder_not_exists(fs):
    source_path = Path(r"C:\target")
    fs.create_dir(source_path)
    fs.create_file(source_path / "t.txt")
    target_folder_path = Path(r"C:\folder")
    move_and_rename_if_exists(source_path, target_folder_path)
    assert((target_folder_path / "target" / "t.txt").exists())
    assert(not source_path.exists())

def test_move_and_rename_if_exists_folder_exists(fs):
    source_path = Path(r"C:\target")
    fs.create_dir(source_path)
    fs.create_file(source_path / "t.txt")
    target_folder_path = Path(r"C:\folder")
    fs.create_dir(target_folder_path / source_path.name)
    move_and_rename_if_exists(source_path, target_folder_path)
    assert((target_folder_path / "target (1)" / "t.txt").exists())
    assert(not source_path.exists())

def test_beautify_album_folder_already_beautified_single_audiofile(fs):
    source_path = Path("C:/root/album")
    fs.create_file(source_path / "t1.mp3")
    fs.create_file(source_path / "Artwork" / "image.jpeg")
    fs.create_file(source_path / "Artwork" / "front.jpeg")
    fs.create_file(source_path / "Misc" / "t1.cue")
    fs.create_file(source_path / "Misc" / "t2.log")
    fs.create_file(source_path / "Misc" / "t.txt")
    beautify_album_folder(source_path)
    assert((source_path / "t1.mp3").exists())
    assert((source_path / "Artwork" / "image.jpeg").exists())
    assert((source_path / "Artwork" / "front.jpeg").exists())
    assert((source_path / "Misc" / "t1.cue").exists())
    assert((source_path / "Misc" / "t2.log").exists())
    assert((source_path / "Misc" / "t.txt").exists())

def test_beautify_album_folder_already_beautified_multiple_audiofiles(fs):
    source_path = Path("C:/album")
    fs.create_file(source_path / "t1.wv")
    fs.create_file(source_path / "t2.wv")
    fs.create_file(source_path / "t3.wv")
    fs.create_file(source_path / "Artwork" / "image.png")
    fs.create_file(source_path / "Misc" / "t1.cue")
    fs.create_file(source_path / "Misc" / "t2.log")
    fs.create_file(source_path / "Misc" / "t.txt")
    beautify_album_folder(source_path)
    assert((source_path / "t1.wv").exists())
    assert((source_path / "t2.wv").exists())
    assert((source_path / "t3.wv").exists())
    assert((source_path / "Artwork" / "image.png").exists())
    assert((source_path / "Misc" / "t1.cue").exists())
    assert((source_path / "Misc" / "t2.log").exists())
    assert((source_path / "Misc" / "t.txt").exists())

def test_beautify_album_folder_audio_image(fs):
    source_path = Path("C:/album")
    fs.create_file(source_path / "t1.wv")
    fs.create_file(source_path / "t1.cue")
    fs.create_file(source_path / "t1.log")
    fs.create_file(source_path / "image.png")
    fs.create_file(source_path / "folder.jpg")
    fs.create_file(source_path / "t.txt")
    fs.create_file(source_path / "a.cue")
    fs.create_file(source_path / "b.log")
    beautify_album_folder(source_path)
    assert((source_path / "t1.wv").exists())
    assert((source_path / "t1.cue").exists())
    assert((source_path / "t1.log").exists())
    assert((source_path / "Artwork" / "image.png").exists())
    assert((source_path / "Artwork" / "folder.jpg").exists())
    assert((source_path / "Misc" / "t.txt").exists())
    assert((source_path / "Misc" / "a.cue").exists())
    assert((source_path / "Misc" / "b.log").exists())

def test_beautify_album_folder_with_existing_folders(fs):
    source_path = Path("C:/album")
    fs.create_dir(source_path / "artwork")
    fs.create_file(source_path / "artwork" / "image.png")
    fs.create_dir(source_path / "misc")
    fs.create_file(source_path / "some_folder" / "q.q")
    fs.create_file(source_path / "t1.wv")
    fs.create_file(source_path / "t1.cue")
    fs.create_file(source_path / "t1.log")
    fs.create_file(source_path / "image.png")
    fs.create_file(source_path / "folder.jpg")
    fs.create_file(source_path / "t.txt")
    fs.create_file(source_path / "a.cue")
    fs.create_file(source_path / "b.log")
    beautify_album_folder(source_path)
    assert((source_path / "t1.wv").exists())
    assert((source_path / "t1.cue").exists())
    assert((source_path / "t1.log").exists())
    assert((source_path / "Artwork" / "image.png").exists())
    assert((source_path / "Artwork" / "image (1).png").exists())
    assert((source_path / "Artwork" / "folder.jpg").exists())
    assert((source_path / "Misc" / "t.txt").exists())
    assert((source_path / "Misc" / "a.cue").exists())
    assert((source_path / "Misc" / "b.log").exists())
    assert((source_path / "Misc" / "some_folder" / "q.q").exists())
    assert(not (source_path / "some_folder").exists())

def test_beautify_album_folder_general(fs):
    source_path = Path("C:/album")
    fs.create_dir(source_path / "artwork")
    fs.create_dir(source_path / "misc")
    fs.create_file(source_path / "t1.wv")
    fs.create_file(source_path / "t1.cue")
    fs.create_file(source_path / "t1.log")
    fs.create_file(source_path / "image.png")
    fs.create_file(source_path / "folder.jpg")
    fs.create_file(source_path / "t.txt")
    fs.create_file(source_path / "a.cue")
    fs.create_file(source_path / "b.log")
    beautify_album_folder(source_path)
    assert((source_path / "t1.wv").exists())
    assert((source_path / "t1.cue").exists())
    assert((source_path / "t1.log").exists())
    assert((source_path / "Artwork" / "image.png").exists())
    assert((source_path / "Artwork" / "folder.jpg").exists())
    assert((source_path / "Misc" / "t.txt").exists())
    assert((source_path / "Misc" / "a.cue").exists())
    assert((source_path / "Misc" / "b.log").exists())



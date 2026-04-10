import pytest

from src.infra.drive_downloader import DriveDownloader
from src.shared.errors import InvalidUrlError


class TestDriveDownloaderExtractFileId:
    def test_url_valida_com_sharing(self):
        url = "https://drive.google.com/file/d/1KaIwfTZzG-Da9ueQLNnhYxctT2K83rJy/view?usp=sharing"
        file_id = DriveDownloader._extract_file_id(url)
        assert file_id == "1KaIwfTZzG-Da9ueQLNnhYxctT2K83rJy"

    def test_url_valida_sem_query_params(self):
        url = "https://drive.google.com/file/d/abc123_-XYZ/view"
        file_id = DriveDownloader._extract_file_id(url)
        assert file_id == "abc123_-XYZ"

    def test_url_invalida_lanca_erro(self):
        with pytest.raises(InvalidUrlError):
            DriveDownloader._extract_file_id("https://google.com")

    def test_url_vazia_lanca_erro(self):
        with pytest.raises(InvalidUrlError):
            DriveDownloader._extract_file_id("")


# Esse arquivo possui código gerado com IA

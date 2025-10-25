import os
import sys
import shutil
import pytest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import both download functions
from scripts.download_icd11 import download_icd11
from scripts.download_namaste import download_namaste



# COMMON FIXTURE: Clean data folder before and after each test

@pytest.fixture(autouse=True)
def clean_data_folder():
    if os.path.exists("data"):
        shutil.rmtree("data")
    yield
    if os.path.exists("data"):
        shutil.rmtree("data")


# TESTS FOR download_icd11.py

def test_icd11_data_folder_created():
    """Test that 'data' folder is created when running download_icd11"""
    download_icd11()
    assert os.path.exists("data"), "Data folder was not created by download_icd11."


def test_icd11_file_downloaded():
    """Test that ICD-11.csv is downloaded"""
    download_icd11()
    file_path = os.path.join("data", "ICD-11.csv")
    assert os.path.exists(file_path), "ICD-11.csv was not downloaded."


def test_icd11_file_already_exists(monkeypatch):
    """Test that function skips downloading if file exists"""
    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", "ICD-11.csv")
    with open(file_path, "w") as f:
        f.write("dummy content")

    messages = []
    monkeypatch.setattr("builtins.print", lambda m: messages.append(m))

    download_icd11()

    assert any("already exists" in m for m in messages), "ICD-11 existing file not detected."


def test_icd11_download_failure(monkeypatch):
    """Simulate a download failure for ICD-11"""
    import requests
    import scripts.download_icd11 as module

    class FakeResponse:
        def raise_for_status(self):
            raise requests.RequestException("Download failed")

        @property
        def content(self):
            return b""

    monkeypatch.setattr(module.requests, "get", lambda url: FakeResponse())
    messages = []
    monkeypatch.setattr("builtins.print", lambda m: messages.append(m))

    module.download_icd11()

    assert any("Failed to download" in m for m in messages), "Failure message not printed for ICD-11."


# TESTS FOR download_namaste.py
if os.path.exists("data/namaste_siddha_morbidity.csv"):
    print("Data already exists — skipping download.")
else:
    download_namaste()

def test_namaste_data_folder_created():
    """Test that 'data' folder is created"""
    download_namaste()
    assert os.path.exists("data"), "Data folder was not created by download_namaste."


def test_namaste_file_downloaded(monkeypatch):
    """Simulate successful file download for namaste"""
    import scripts.download_namaste as module

    class FakeResponse:
        def raise_for_status(self): pass
        @property
        def content(self): return b"dummy data"

    # Mock requests.get
    monkeypatch.setattr(module.requests, "get", lambda url: FakeResponse())

    download_namaste()

    for fname in [
        "namaste_siddha_morbidity.csv",
        "namaste_unani_morbidity.csv",
        "namaste_ayurveda_morbidity.csv",
        "ayurveda_standard_terminology.csv"
    ]:
        assert os.path.exists(os.path.join("data", fname)), f"{fname} was not created."


def test_namaste_file_already_exists(monkeypatch):
    """Test that already existing files are skipped"""
    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", "namaste_siddha_morbidity.csv")
    with open(file_path, "w") as f:
        f.write("dummy")

    messages = []
    monkeypatch.setattr("builtins.print", lambda m: messages.append(m))

    import scripts.download_namaste as module
    module.download_namaste()

    assert any("already exists" in m for m in messages), "Existing namaste file not detected."


def test_namaste_download_failure(monkeypatch):
    """Simulate a download failure for namaste"""
    import scripts.download_namaste as module
    import requests

    class FakeResponse:
        def raise_for_status(self):
            raise requests.RequestException("Download failed")
        @property
        def content(self):
            return b""

    monkeypatch.setattr(module.requests, "get", lambda url: FakeResponse())
    messages = []
    monkeypatch.setattr("builtins.print", lambda m: messages.append(m))

    module.download_namaste()

    assert any("Failed to download" in m for m in messages), "Failure message not printed for namaste."

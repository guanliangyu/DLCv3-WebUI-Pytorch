from pathlib import Path

from src.core.utils.file_utils import upload_files


class DummyUploadedFile:
    def __init__(self, name: str, content: bytes = b"test-data"):
        self.name = name
        self._content = content

    def getbuffer(self) -> bytes:
        return self._content


def test_upload_files_rejects_path_traversal(monkeypatch, tmp_path: Path) -> None:
    uploads = [
        DummyUploadedFile("../../escape.mp4"),
        DummyUploadedFile("safe.mp4"),
    ]
    errors = []
    successes = []

    monkeypatch.setattr(
        "src.core.utils.file_utils.st.file_uploader",
        lambda *args, **kwargs: uploads,
    )
    monkeypatch.setattr("src.core.utils.file_utils.st.error", errors.append)
    monkeypatch.setattr("src.core.utils.file_utils.st.success", successes.append)

    saved_files = upload_files(str(tmp_path))

    assert len(saved_files) == 1
    assert Path(saved_files[0]).resolve() == (tmp_path / "safe.mp4").resolve()
    assert (tmp_path / "safe.mp4").exists()
    assert not (tmp_path.parent / "escape.mp4").exists()
    assert errors, "Traversal-like filenames should be rejected."
    assert successes, "Valid files should still be accepted."

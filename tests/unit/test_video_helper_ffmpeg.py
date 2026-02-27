from src.core.helpers.video_helper import (
    build_ffmpeg_reencode_command,
    preview_original_frame,
    run_ffmpeg_reencode,
)


def test_build_ffmpeg_reencode_command_uses_arg_list() -> None:
    input_path = "/tmp/input video.mp4"
    output_path = "/tmp/output video.mp4"

    command = build_ffmpeg_reencode_command(input_path, output_path)

    assert isinstance(command, list)
    assert command[:4] == ["ffmpeg", "-y", "-i", input_path]
    assert command[-1] == output_path


def test_run_ffmpeg_reencode_uses_subprocess_run(monkeypatch) -> None:
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs

    monkeypatch.setattr("src.core.helpers.video_helper.subprocess.run", fake_run)

    run_ffmpeg_reencode("/tmp/in.mp4", "/tmp/out.mp4")

    assert captured["cmd"][0] == "ffmpeg"
    assert captured["kwargs"]["check"] is True
    assert captured["kwargs"]["text"] is True
    assert "shell" not in captured["kwargs"]


def test_preview_original_frame_releases_capture_on_early_return(monkeypatch) -> None:
    class FakeCapture:
        def __init__(self):
            self.released = False

        def get(self, _):
            return 10

        def set(self, *_):
            return None

        def read(self):
            return True, [["pixel"]]

        def release(self):
            self.released = True

    fake_capture = FakeCapture()

    monkeypatch.setattr(
        "src.core.helpers.video_helper.cv2.VideoCapture", lambda *_: fake_capture
    )
    monkeypatch.setattr(
        "src.core.helpers.video_helper.cv2.rectangle", lambda *a, **k: None
    )
    monkeypatch.setattr(
        "src.core.helpers.video_helper.cv2.cvtColor", lambda frame, _: frame
    )

    result = preview_original_frame("dummy.mp4", x=0, y=0, width=1, height=1)

    assert result == [["pixel"]]
    assert fake_capture.released is True

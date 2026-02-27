from pathlib import Path

from src.core.config.config_manager import initialize_authenticator, load_config


def test_load_config_returns_dict_for_valid_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        (
            "credentials:\n"
            "  usernames:\n"
            "    tester:\n"
            "      email: tester@example.com\n"
            "      name: Tester\n"
            "      password: test\n"
            "cookie:\n"
            "  name: test_cookie\n"
            "  key: test_key\n"
            "  expiry_days: 7\n"
        ),
        encoding="utf-8",
    )

    result = load_config(str(config_path))

    assert isinstance(result, dict)
    assert result["cookie"]["name"] == "test_cookie"


def test_load_config_returns_none_when_file_missing(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing_config.yaml"
    assert load_config(str(missing_path)) is None


def test_initialize_authenticator_returns_none_for_incomplete_config() -> None:
    assert initialize_authenticator({"credentials": {}}) is None
    assert initialize_authenticator({"cookie": {}}) is None


def test_initialize_authenticator_passes_expected_arguments(monkeypatch) -> None:
    captured = {}
    sentinel = object()

    def fake_authenticate(credentials, cookie_name, cookie_key, expiry_days):
        captured["credentials"] = credentials
        captured["cookie_name"] = cookie_name
        captured["cookie_key"] = cookie_key
        captured["expiry_days"] = expiry_days
        return sentinel

    monkeypatch.setattr(
        "src.core.config.config_manager.stauth.Authenticate",
        fake_authenticate,
    )

    config = {
        "credentials": {"usernames": {"tester": {"password": "hashed"}}},
        "cookie": {"name": "cookie_name", "key": "cookie_key", "expiry_days": 30},
    }

    result = initialize_authenticator(config)

    assert result is sentinel
    assert captured["cookie_name"] == "cookie_name"
    assert captured["cookie_key"] == "cookie_key"
    assert captured["expiry_days"] == 30

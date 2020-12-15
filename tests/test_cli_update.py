import json
import pytest

from click.testing import CliRunner
from unittest import mock

from mapbox_tilesets.scripts.cli import update


class MockResponse:
    def __init__(self, mock_json, status_code):
        self.text = json.dumps(mock_json)
        self._json = mock_json
        self.status_code = status_code

    def MockResponse(self):
        return self

    def json(self):
        return self._json


@pytest.mark.usefixtures("token_environ")
@mock.patch("requests.Session.patch")
def test_cli_patch(mock_request_patch):
    runner = CliRunner()

    # sends expected request
    mock_request_patch.return_value = MockResponse("", 204)
    result = runner.invoke(
        update,
        [
            "test.id",
            "--name=hola",
            "--description=hello world",
            "--privacy=private",
            '--attribution=[{"text":"natural earth data","link":"https://naturalearthdata.com"}]',
            "--accept_pricing"
        ],
    )

    mock_request_patch.assert_called_with(
        "https://api.mapbox.com/tilesets/v1/test.id?access_token=pk.eyJ1IjoidGVzdC11c2VyIn0K",
        json={
            "name": "hola",
            "description": "hello world",
            "private": True,
            "attribution": [
                {"text": "natural earth data", "link": "https://naturalearthdata.com"}
            ],
        },
    )
    assert result.exit_code == 0
    assert result.output == ""


@pytest.mark.usefixtures("token_environ")
@mock.patch("requests.Session.patch")
@mock.patch("click.confirm")
def test_cli_patch_no_options(mock_click_confirm, mock_request_patch):
    runner = CliRunner()
    mock_click_confirm.return_value = "y"
    # sends expected request
    mock_request_patch.return_value = MockResponse("", 204)
    result = runner.invoke(update, ["test.id"])
    mock_click_confirm.assert_called_with(
        "There may be costs associated with uploading and hosting this tileset. Please review the pricing documentation:  https://docs.mapbox.com/accounts/overview/pricing/#tilesets\n To opt out of pricing warnings, pass the --accept_pricing flag. \n Do you want to continue?"
    )
    mock_request_patch.assert_called_with(
        "https://api.mapbox.com/tilesets/v1/test.id?access_token=pk.eyJ1IjoidGVzdC11c2VyIn0K",
        json={},
    )
    assert result.exit_code == 0
    assert result.output == ""


@pytest.mark.usefixtures("token_environ")
@mock.patch("click.confirm")
def test_cli_patch_invalid_json(mock_click_confirm):
    runner = CliRunner()
    mock_click_confirm.return_value = "y"
    # send invalid json request
    result = runner.invoke(update, ["test.id", "--attribution=invalid json"])

    assert result.exit_code == 1
    assert "Unable to parse attribution JSON" in result.output

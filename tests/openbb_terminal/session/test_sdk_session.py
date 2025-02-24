# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
from unittest.mock import patch

import pytest

# IMPORTATION INTERNAL
from openbb_terminal.session import sdk_session
from openbb_terminal.session.session_model import LoginStatus
from openbb_terminal.session.user import User

TEST_SESSION = {
    "access_token": "test_token",
    "token_type": "bearer",
    "uuid": "test_uuid",
}


@pytest.mark.parametrize(
    "email, password, token, save",
    [
        (
            "test_email",
            "test_pass",
            "test_token",
            True,
        ),
    ],
)
def test_get_session_exception(email: str, password: str, token: str, save: bool):
    path = "openbb_terminal.session.sdk_session."
    with patch(path + "session_model.create_session") as mock_create_session:
        with patch(
            path + "session_model.create_session_from_token"
        ) as mock_create_session_from_token:
            mock_create_session.return_value = {}
            mock_create_session_from_token.return_value = {}

            with pytest.raises(Exception):
                sdk_session.get_session(
                    email=email, password=password, token=token, save=save
                )

            mock_create_session.assert_called_once_with(email, password, save)
            mock_create_session_from_token.assert_called_once_with(token, save)


@pytest.mark.parametrize(
    "email, password, token, save",
    [
        (
            "test_email",
            "test_pass",
            "test_token",
            True,
        ),
    ],
)
def test_get_session(email: str, password: str, token: str, save: bool):
    path = "openbb_terminal.session.sdk_session."
    with patch(path + "session_model.create_session") as mock_create_session:
        mock_create_session.return_value = TEST_SESSION

        sdk_session.get_session(email=email, password=password, token=token, save=save)
        mock_create_session.assert_called_once_with(email, password, save)


@pytest.mark.parametrize(
    "email, password, token, save",
    [
        (
            "test_email",
            "test_pass",
            "test_token",
            True,
        ),
    ],
)
def test_get_session_from_token(email: str, password: str, token: str, save: bool):
    path = "openbb_terminal.session.sdk_session."
    with patch(
        path + "session_model.create_session_from_token"
    ) as mock_create_session_from_token:
        mock_create_session_from_token.return_value = TEST_SESSION

        sdk_session.get_session(email=email, password=password, token=token, save=save)
        mock_create_session_from_token.assert_called_once_with(token, save)


@pytest.mark.parametrize(
    "email, password, token, keep_session, has_session, status",
    [
        (
            "test_email",
            "test_pass",
            "test_token",
            True,
            False,
            LoginStatus.SUCCESS,
        ),
        (
            "test_email",
            "test_pass",
            "test_token",
            True,
            True,
            LoginStatus.SUCCESS,
        ),
        (
            "test_email",
            "test_pass",
            "test_token",
            True,
            False,
            LoginStatus.FAILED,
        ),
        (
            "test_email",
            "test_pass",
            "test_token",
            True,
            False,
            LoginStatus.NO_RESPONSE,
        ),
    ],
)
def test_login(
    mocker,
    email: str,
    password: str,
    token: str,
    keep_session: bool,
    has_session: bool,
    status: LoginStatus,
):
    path = "openbb_terminal.session.sdk_session."
    mock_login = mocker.patch(path + "session_model.login")
    mock_local_get_session = mocker.patch(path + "Local.get_session")
    mock_hub_get_session = mocker.patch(path + "get_session")

    if has_session:
        mock_local_get_session.return_value = TEST_SESSION
    else:
        mock_local_get_session.return_value = None

    mock_hub_get_session.return_value = TEST_SESSION
    mock_login.return_value = status

    if status in [LoginStatus.FAILED, LoginStatus.NO_RESPONSE]:
        with pytest.raises(Exception):
            sdk_session.login(
                email=email,
                password=password,
                token=token,
                keep_session=keep_session,
            )
    else:
        sdk_session.login(
            email=email, password=password, token=token, keep_session=keep_session
        )

    mock_local_get_session.assert_called_once()
    if has_session:
        mock_hub_get_session.assert_not_called()
    else:
        mock_hub_get_session.assert_called_once_with(
            email, password, token, keep_session
        )
    mock_login.assert_called_once_with(TEST_SESSION)


def test_logout():
    User.load_user_info(TEST_SESSION, "test@email.com")
    path = "openbb_terminal.session.sdk_session."
    with (patch(path + "session_model.logout") as mock_logout,):
        sdk_session.logout()
        mock_logout.assert_called_once_with(
            auth_header=User.get_auth_header(),
            token=User.get_token(),
            guest=User.is_guest(),
        )


@pytest.mark.record_stdout
def test_whoami_guest():
    sdk_session.whoami()


@pytest.mark.record_stdout
def test_whoami():
    User.load_user_info(
        {
            "token_type": "MOCK_TOKEN_TYPE",
            "access_token": "MOCK_ACCESS_TOKEN",
            "uuid": "MOCK_UUID",
        },
        email="MOCK_EMAIL",
    )
    sdk_session.whoami()

import pytest

from profile_matcher.data_creator import InitialDataCreator


class TestGetClientConfig:

    @pytest.fixture(autouse=True)
    def setup_data(self, session):
        # Since it exists, we use the data creator. Without the initial data creator, we could use a factory helper to
        # allow the easy creation of database object.
        self.__data_creator = InitialDataCreator()
        self.__data_creator.try_create_data(session)

    def test_get_client_config(self, client):
        response = client.get("/api/client-config")
        assert response.status_code == 200
        assert response.json == {
            "client_id": "client_id",
            "client_secret": "client_secret",
            "redirect_uri": "http://localhost:8080/api/client-config/redirect",
            "scopes": ["profile", "email"],
        }
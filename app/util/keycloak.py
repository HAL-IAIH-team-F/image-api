import uuid

from pydantic import BaseModel, field_serializer

from . import urls, err


class WellKnown(BaseModel):
    userinfo_endpoint: str

    @staticmethod
    def fetch(well_known_url: urls.URL):
        return (well_known_url
                .to_request()
                .content_type(urls.ContentType.JSON)
                .add_header("User-Agent", "Application")
                .fetch()
                .json_model(WellKnown)
                )


class KeycloakUserProfile(BaseModel):
    sub: uuid.UUID
    email_verified: bool
    preferred_username: str
    email: str

    @field_serializer("sub")
    def serialize_date(self, sub: uuid.UUID) -> str:
        return str(sub)

    @staticmethod
    def fetch(well_known: WellKnown, access_token: str):
        return (urls.URL.by_str(well_known.userinfo_endpoint)
                .to_request()
                .authorization(urls.BearerAuthorization(access_token))
                .add_header("User-Agent", "Application")
                .fetch()
                .on_status_code(401, lambda s: err.ErrorIds.INVALID_KEYCLOAK_TOKEN.to_exception().raise_self())
                .json_model(KeycloakUserProfile)
                )

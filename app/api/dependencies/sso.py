import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError

from app.schemas.auth import User
from app.services.auth_service import PrivateAuthService

logger = logging.getLogger("app")


class SSOAuth(HTTPBearer):
    async def __call__(  # type: ignore
        self,
        request: Request,
        sso_service: PrivateAuthService = Depends(PrivateAuthService),
    ) -> User:
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(
            request
        )
        if not credentials:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unauthorized access. Credentials are mandatory.",
                )
            return User.anonymous()
        try:
            auth_info = sso_service.introspect(credentials.credentials)
            user = User(**auth_info)
            # user.referer = request.headers.get("referer")
            # user.ip_address = request.client
        except ValidationError as error:
            logger.error(f"SSOAuth response validation error: {str(error)}")
            return User.anonymous()
        return user


sso_auth = SSOAuth(auto_error=True)
optional_sso_auth = SSOAuth(auto_error=False)

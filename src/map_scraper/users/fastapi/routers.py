from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from map_scraper.shared.infra import SqlAlchemyRepository
from map_scraper.users import (
    authenticate_user, User,
    create_access_token, TokenResponse,
    create_account, CreateAccountCommand,
)


def add_users_router(app: FastAPI):
    @app.post('/token')
    async def login(
            request: Request,
            form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> TokenResponse:
        auth_res = await authenticate_user(request.state.db, form_data.username, form_data.password)
        
        if not auth_res.is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect username or password',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        access_token = await create_access_token(form_data.username)
        return access_token

    @app.post('/sign-up')
    async def sign_up(
            request: Request,
            command: CreateAccountCommand):
        await create_account(
            SqlAlchemyRepository(request.state.db, User), command
        )
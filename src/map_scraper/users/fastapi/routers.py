from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from map_scraper.shared.fastapi import ApiResponse
from map_scraper.users.app import (
    create_access_token, TokenResponse,
    create_account, CreateAccountCommand,
)

from map_scraper.users.app import authenticate_user


def add_users_router(app: FastAPI):
    @app.post('/sign-up',
              response_model=ApiResponse)
    async def sign_up(
            request: Request,
            command: CreateAccountCommand):
        await create_account(request.state.db, command)
        return ApiResponse.success()

    @app.post('/token',
              response_model=TokenResponse)
    async def login(
            request: Request,
            form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        await authenticate_user(request.state.db, form_data.username, form_data.password)
        access_token = await create_access_token(form_data.username)
        return access_token

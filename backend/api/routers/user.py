from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from typing import Annotated

from rope.api.auth import verify_user, verify_admin
from rope.api import database
from rope.api.models import BaseUser, FullUser


router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get("/current/")
def get_current_user(current_user: Annotated[dict, Depends(verify_user)]) -> BaseUser:
    return current_user


@router.get("/", dependencies=[Depends(verify_admin)])
def get_users(db: Session = Depends(database.get_db)) -> list[FullUser]:
    users = database.get_all_users(db)
    return users


@router.post("/", dependencies=[Depends(verify_admin)])
def create_user(user: BaseUser, db: Session = Depends(database.get_db)) -> FullUser:
    new_user = database.create_user(db, user)
    return new_user


@router.put("/{id}/", dependencies=[Depends(verify_admin)])
def update_user(user: FullUser, db: Session = Depends(database.get_db)) -> FullUser:
    updated_user = database.update_user(db, user)
    return updated_user


@router.delete("/{id}/", dependencies=[Depends(verify_admin)])
def delete_user(id: int, db: Session = Depends(database.get_db)):
    row_deleted = database.delete_user(db, id)
    if row_deleted == 0:
        raise HTTPException(
            status_code=404, detail=f"User with the id: {id} does not exist"
        )

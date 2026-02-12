from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from models import PlayerSave
from schemas import SavePayload
from auth import get_current_user, get_db

router = APIRouter(prefix="/save", tags=["save"])


@router.get("/load")
def load_save(
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    save = db.query(PlayerSave).filter(PlayerSave.user_id == user.id).first()
    if not save:
        return {"save_data": None}

    return {"save_data": save.save_data}


@router.post("/save")
def save_game(
    payload: SavePayload,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    save = db.query(PlayerSave).filter(PlayerSave.user_id == user.id).first()

    if not save:
        save = PlayerSave(
            user_id=user.id,
            save_data=payload.save_data
        )
        db.add(save)
    else:
        save.save_data = payload.save_data
        save.updated_at = datetime.utcnow()

    db.commit()
    return {"status": "ok"}
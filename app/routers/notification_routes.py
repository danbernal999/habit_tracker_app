from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import logging

from app.database.config import get_db
from app.models import models
from app.schemas import schemas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[schemas.Notification])
def get_notifications(
    user_id: int,
    include_read: bool = True,
    db: Session = Depends(get_db)
):
    """
    Obtener notificaciones del usuario autenticado.
    """
    try:
        logger.info(f"Obteniendo notificaciones para el usuario {user_id}")

        query = db.query(models.Notification).options(joinedload(models.Notification.actions)).filter(models.Notification.user_id == user_id)
        if not include_read:
            query = query.filter(models.Notification.is_read.is_(False))

        notifications = query.order_by(models.Notification.created_at.desc()).all()
        logger.info(f"Encontradas {len(notifications)} notificaciones")
        return notifications
    except Exception as exc:
        logger.error(f"Error al obtener notificaciones: {exc}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/unread/count")
def get_unread_count(user_id: int, db: Session = Depends(get_db)):
    """
    Obtener el número de notificaciones sin leer.
    """
    try:
        count = db.query(models.Notification).filter(
            models.Notification.user_id == user_id,
            models.Notification.is_read.is_(False)
        ).count()
        logger.info(f"Usuario {user_id} tiene {count} notificaciones sin leer")
        return {"unread_count": count}
    except Exception as exc:
        logger.error(f"Error al contar notificaciones: {exc}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/", response_model=schemas.Notification, status_code=status.HTTP_201_CREATED)
def create_notification(notification: schemas.NotificationCreate, db: Session = Depends(get_db)):
    """
    Crear una notificación manualmente.
    """
    try:
        user = db.query(models.User).filter(models.User.id == notification.user_id).first()
        if not user:
            logger.warning(f"Usuario {notification.user_id} no encontrado al crear notificación")
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        db_notification = models.Notification(
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            is_read=notification.is_read
        )

        for action in notification.actions:
            db_notification.actions.append(
                models.NotificationAction(
                    action_type=action.action_type,
                    label=action.label,
                    payload=action.payload
                )
            )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        db_notification.actions  # Fuerza carga de acciones

        logger.info(f"Notificación creada para usuario {notification.user_id}")
        return db_notification
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error al crear notificación: {exc}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{notification_id}/read", response_model=schemas.Notification)
def mark_notification_as_read(notification_id: int, db: Session = Depends(get_db)):
    """
    Marcar una notificación como leída.
    """
    try:
        notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
        if notification is None:
            logger.warning(f"Notificación {notification_id} no encontrada")
            raise HTTPException(status_code=404, detail="Notificación no encontrada")

        notification.is_read = True
        db.commit()
        db.refresh(notification)
        notification.actions  # Fuerza la carga de acciones
        logger.info(f"Notificación {notification_id} marcada como leída")
        return notification
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error al actualizar notificación: {exc}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/mark-all/read")
def mark_all_notifications_as_read(user_id: int, db: Session = Depends(get_db)):
    """
    Marcar todas las notificaciones del usuario como leídas.
    """
    try:
        updated = db.query(models.Notification).filter(
            models.Notification.user_id == user_id,
            models.Notification.is_read.is_(False)
        ).update({"is_read": True})
        db.commit()
        logger.info(f"{updated} notificaciones marcadas como leídas para el usuario {user_id}")
        return {"updated": updated}
    except Exception as exc:
        logger.error(f"Error al marcar notificaciones como leídas: {exc}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

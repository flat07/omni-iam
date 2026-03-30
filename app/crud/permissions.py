# app/crud/permissions.py
from sqlalchemy import select
from app.models.identity import Permission, GroupPermission, UserGroup


def get_user_permissions(db, user_id):

    query = (
        select(Permission.code)
        .join(GroupPermission, Permission.id == GroupPermission.permission_id)
        .join(UserGroup, UserGroup.group_id == GroupPermission.group_id)
        .where(UserGroup.user_id == user_id)
    )

    rows = db.execute(query).all()

    return [r[0] for r in rows]
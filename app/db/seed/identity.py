from sqlalchemy.orm import Session
from app.models.identity import User, Group, Permission, UserGroup, GroupPermission
from app.models.organization import Location, Department
import hashlib


def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


PERMISSIONS = [
    "tickets:read",
    "tickets:create",
    "tickets:update",
    "tickets:delete",
    "users:read",
    "users:create",
    "users:update",
    "users:delete",
]


GROUPS = {
    "Admin": PERMISSIONS,
    "Manager": [
        "tickets:read",
        "tickets:create",
        "tickets:update",
    ],
    "Staff": [
        "tickets:read",
        "tickets:create",
    ],
}


def seed_permissions(db: Session, vendor):

    created = []

    for code in PERMISSIONS:

        p = db.query(Permission).filter(Permission.code == code).first()

        if not p:
            p = Permission(
                code=code,
                vendor_id=vendor.id
            )
            db.add(p)
            created.append(p)

    db.commit()

    print("✅ Permissions seeded")

    return db.query(Permission).all()


def seed_groups(db: Session, vendor):

    groups = {}

    for name in GROUPS.keys():

        g = db.query(Group).filter(Group.name == name).first()

        if not g:
            g = Group(
                name=name,
                vendor_id=vendor.id
            )
            db.add(g)

        db.commit()
        db.refresh(g)

        groups[name] = g

    print("✅ Groups seeded")

    return groups


def seed_group_permissions(db: Session, groups, permissions):

    permission_map = {p.code: p for p in permissions}

    for group_name, perms in GROUPS.items():

        group = groups[group_name]

        for code in perms:

            perm = permission_map[code]

            exists = db.query(GroupPermission).filter(
                GroupPermission.group_id == group.id,
                GroupPermission.permission_id == perm.id
            ).first()

            if not exists:

                db.add(GroupPermission(
                    group_id=group.id,
                    permission_id=perm.id
                ))

    db.commit()

    print("✅ Group permissions seeded")


def seed_admin_user(db: Session, vendor):

    user = db.query(User).filter(User.email == "admin@demo.com").first()

    if user:
        return user

    location = db.query(Location).filter(Location.vendor_id == vendor.id).first()
    department = db.query(Department).filter(
        Department.vendor_id == vendor.id,
        Department.name == "IT"
    ).first()

    user = User(
        email="admin@demo.com",
        password_hash=hash_password("admin"),
        vendor_id=vendor.id,
        location_id=location.id,
        department_id=department.id,
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    print("✅ Admin user created")

    return user


def attach_admin_group(db: Session, user, groups):

    admin_group = groups["Admin"]

    exists = db.query(UserGroup).filter(
        UserGroup.user_id == user.id,
        UserGroup.group_id == admin_group.id
    ).first()

    if not exists:

        db.add(UserGroup(
            user_id=user.id,
            group_id=admin_group.id
        ))

        db.commit()

    print("✅ Admin assigned to Admin group")


def seed_housekeeping_users(db: Session, vendor, groups):

    location = db.query(Location).filter(
        Location.vendor_id == vendor.id
    ).first()

    department = db.query(Department).filter(
        Department.vendor_id == vendor.id,
        Department.name == "Housekeeping"
    ).first()

    users = [
        ("manager@demo.com", "Manager"),
        ("staff1@demo.com", "Staff"),
        ("staff2@demo.com", "Staff"),
        ("staff3@demo.com", "Staff"),
    ]

    for email, role in users:

        user = db.query(User).filter(User.email == email).first()

        if not user:
            user = User(
                email=email,
                password_hash=hash_password("admin"),
                vendor_id=vendor.id,
                location_id=location.id,
                department_id=department.id,
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 👉 Attach group
        group = groups.get(role)

        if not group:
            continue

        exists = db.query(UserGroup).filter(
            UserGroup.user_id == user.id,
            UserGroup.group_id == group.id
        ).first()

        if not exists:
            db.add(UserGroup(
                user_id=user.id,
                group_id=group.id
            ))

    db.commit()

    print("✅ Housekeeping users seeded with groups")


def seed_identity(db: Session, vendor):

    permissions = seed_permissions(db, vendor)

    groups = seed_groups(db, vendor)

    seed_group_permissions(db, groups, permissions)

    admin = seed_admin_user(db, vendor)

    attach_admin_group(db, admin, groups)
    seed_housekeeping_users(db, vendor, groups)
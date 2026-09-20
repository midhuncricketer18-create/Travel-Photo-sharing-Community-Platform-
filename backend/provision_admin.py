import argparse
import getpass

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision a local administrator account")
    parser.add_argument("--email", required=True)
    parser.add_argument("--promote-existing", action="store_true")
    args = parser.parse_args()

    password = getpass.getpass("Admin password: ")
    if len(password) < 8:
        raise SystemExit("Admin password must be at least 8 characters")

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == args.email.lower()))
        if user is not None and user.role != UserRole.ADMINISTRATOR and not args.promote_existing:
            raise SystemExit("Account exists; rerun with --promote-existing to change its role")

        if user is None:
            user = User(
                email=args.email.lower(),
                hashed_password=hash_password(password),
                role=UserRole.ADMINISTRATOR,
            )
            db.add(user)
        else:
            user.hashed_password = hash_password(password)
            user.role = UserRole.ADMINISTRATOR
            user.is_active = True

        db.commit()

    print(f"Administrator provisioned: {args.email.lower()}")


if __name__ == "__main__":
    main()
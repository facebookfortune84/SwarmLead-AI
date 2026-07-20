from core.config import *

from core.persistence.session import SessionLocal
from interfaces.api.auth.user_service import UserCreate, UserService

db = SessionLocal()

try:
    service = UserService(db)

    email = "robertdemottojr83@gmail.com"

    existing = service.get_user_by_email(email)

    if existing:
        print(f"User already exists: {email}")

    else:
        user = service.create_user(
            UserCreate(
                email=email,
                password="Flossie1984!",
                full_name="Robert Demotto Jr",
            )
        )

        user.role = "admin"

        db.commit()
        db.refresh(user)

        print(f"Created admin: {email}")

finally:
    db.close()

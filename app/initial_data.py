from .core.database import SessionLocal, engine
from .core import models
from .core.security import get_password_hash

def init_db():
    db = SessionLocal()
    try:
        # Drop and recreate all tables for a clean slate during development
        # In a production environment, you would use migrations (e.g., with Alembic)
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)

        # --- Create Default Branch ---
        default_branch_name = "Matriz"
        db_branch = db.query(models.Branch).filter(models.Branch.name == default_branch_name).first()
        if not db_branch:
            db_branch = models.Branch(name=default_branch_name, location="Sede Principal")
            db.add(db_branch)
            db.commit()
            db.refresh(db_branch)
            print(f"Default branch '{default_branch_name}' created.")
        else:
            print(f"Default branch '{default_branch_name}' already exists.")

        # --- Create Master Admin User ---
        master_user_email = "taynanleal359@gmail.com"
        db_user = db.query(models.User).filter(models.User.email == master_user_email).first()

        if not db_user:
            hashed_password = get_password_hash("123456")
            db_user = models.User(
                email=master_user_email,
                hashed_password=hashed_password,
                is_active=True,
                profile=models.UserProfile.ADMIN
            )
            # Associate with the default branch
            db_user.branches.append(db_branch)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            print(f"Master user '{master_user_email}' created as ADMIN and assigned to '{default_branch_name}'.")
        else:
            # Ensure existing user is admin and assigned to the branch
            if db_user.profile != models.UserProfile.ADMIN:
                db_user.profile = models.UserProfile.ADMIN
                print(f"Master user '{master_user_email}' has been promoted to ADMIN.")
            
            if db_branch not in db_user.branches:
                db_user.branches.append(db_branch)
                print(f"Master user '{master_user_email}' has been assigned to '{default_branch_name}'.")
            
            db.commit()
            print(f"Master user '{master_user_email}' is correctly configured.")

    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database with default data...")
    init_db()
    print("Database initialization complete.")

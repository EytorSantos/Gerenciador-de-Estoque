from app.core.database.database import SessionLocal, engine
from app.core.models import models
from app.core.models.models import User, UserRole
from app.core.security.jwt import get_password_hash
from app.core.security.two_factor_auth import generate_totp_secret

# Create tables
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    # Check for existing admin user by email
    admin = db.query(User).filter(User.email == 'admin@example.com').first()

    if admin:
        # Update existing admin user
        if admin.username != 'admin_test':
            admin.username = 'admin_test'
        if admin.hashed_password != get_password_hash('admin123'):
            admin.hashed_password = get_password_hash('admin123')
        if not admin.is_active:
            admin.is_active = True
        if admin.role != UserRole.ADMIN:
            admin.role = UserRole.ADMIN
        # Ensure 2FA secret is generated but not enabled by default
        if not admin.two_factor_secret:
            admin.two_factor_secret = generate_totp_secret()
        if admin.is_2fa_enabled:
            admin.is_2fa_enabled = False
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print('Admin user updated successfully')
    else:
        # Create new admin user
        admin = User(
            username='admin_test',
            email='admin@example.com',
            hashed_password=get_password_hash('admin123'),
            role=UserRole.ADMIN,
            is_active=True,
            two_factor_secret=generate_totp_secret(),
            is_2fa_enabled=False
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print('Admin user created successfully')
finally:
    db.close()

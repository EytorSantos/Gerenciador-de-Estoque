from sqlalchemy.orm import Session
from app.core.models.models import User, Profile, Medication, Batch, Movement, Prescription
from app.core.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

class ProfileRepository(BaseRepository[Profile]):
    def __init__(self, db: Session):
        super().__init__(Profile, db)

class MedicationRepository(BaseRepository[Medication]):
    def __init__(self, db: Session):
        super().__init__(Medication, db)

class BatchRepository(BaseRepository[Batch]):
    def __init__(self, db: Session):
        super().__init__(Batch, db)

class MovementRepository(BaseRepository[Movement]):
    def __init__(self, db: Session):
        super().__init__(Movement, db)

class PrescriptionRepository(BaseRepository[Prescription]):
    def __init__(self, db: Session):
        super().__init__(Prescription, db)

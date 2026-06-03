import os
import sys

# Add project root to PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from web.backend.app import create_app
from web.backend.models.db_models import db, Doctor
from web.backend.utils import hash_password

def add_doctor(doctor_id, name, specialization, hospital, password):
    app = create_app()
    with app.app_context():
        if Doctor.query.filter_by(doctor_id=doctor_id).first():
            print(f"Doctor {doctor_id} already exists.")
            return
            
        new_doctor = Doctor(
            doctor_id=doctor_id,
            name=name,
            specialization=specialization,
            hospital_name=hospital,
            password_hash=hash_password(password)
        )
        db.session.add(new_doctor)
        db.session.commit()
        print(f"Doctor {doctor_id} ({name}) added successfully.")

if __name__ == "__main__":
    # Default initial doctor
    add_doctor("DOC001", "Dr. Satish Kumar", "Senior Cardiologist", "Apollo Heart Institute", "doctor123")

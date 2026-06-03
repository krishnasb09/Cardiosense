
import sys
import os

sys.path.append(os.getcwd())

from web.backend.app import create_app, db
from web.backend.models.db_models import Doctor
from web.backend.utils import hash_password

def force_add():
    app = create_app()
    with app.app_context():
        print(f"DB URI from config: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"Engine URL: {db.engine.url}")
        
        # Create tables
        db.create_all()
        
        # Inspect tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables in DB: {tables}")

        if 'doctors' not in tables:
            print("ERROR: 'doctors' table was not created!")
            return

        doctor_id = "DOC001"
        try:
            existing = Doctor.query.filter_by(doctor_id=doctor_id).first()
            
            if existing:
                print(f"Doctor {doctor_id} already exists. Updating password...")
                existing.password_hash = hash_password("doctor123")
                db.session.commit()
                print("Password updated.")
            else:
                print(f"Creating new doctor {doctor_id}...")
                new_doctor = Doctor(
                    doctor_id=doctor_id,
                    name="Dr. Satish Kumar",
                    specialization="Senior Cardiologist",
                    hospital_name="Apollo Heart Institute",
                    password_hash=hash_password("doctor123")
                )
                db.session.add(new_doctor)
                db.session.commit()
                print("Doctor created successfully.")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    force_add()

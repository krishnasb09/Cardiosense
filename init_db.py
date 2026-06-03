
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from web.backend.app import create_app, db
from web.backend.models.db_models import Doctor
from web.backend.utils import hash_password

def init_db():
    app = create_app()
    with app.app_context():
        # Ensure instance folder exists
        instance_path = os.path.join(app.root_path, 'instance')
        # app.root_path points to web/backend, but config uses PROJECT_ROOT/instance
        # Let's use the path from config
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
                print(f"Created database directory: {db_dir}")

        # Create tables if not exist
        db.create_all()
        
        # Check if doctor exists
        doctor_id = "DOC001"
        if Doctor.query.filter_by(doctor_id=doctor_id).first():
            print(f"Doctor {doctor_id} already exists.")
        else:
            # Create doctor
            new_doctor = Doctor(
                doctor_id=doctor_id,
                name="Dr. Satish Kumar",
                specialization="Senior Cardiologist",
                hospital_name="Apollo Heart Institute",
                password_hash=hash_password("doctor123")
            )
            db.session.add(new_doctor)
            db.session.commit()
            print(f"Doctor {doctor_id} created successfully with password 'doctor123'.")

if __name__ == "__main__":
    init_db()

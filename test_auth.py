
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from web.backend.app import create_app, db
from web.backend.models.db_models import Doctor
from web.backend.utils import check_password, hash_password

def debug_auth():
    app = create_app()
    with app.app_context():
        print(f"DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        doctor = Doctor.query.filter_by(doctor_id="DOC001").first()
        if not doctor:
            print("❌ Doctor DOC001 NOT FOUND in database.")
            return

        print(f"✅ Doctor Found: {doctor.name}")
        print(f"Stored Hash: {doctor.password_hash}")
        
        # Test Password
        password = "doctor123"
        is_valid = check_password(password, doctor.password_hash)
        
        if is_valid:
            print(f"✅ Password '{password}' is VALID.")
        else:
            print(f"❌ Password '{password}' is INVALID.")
            
            # Debug: Create new hash and compare
            new_hash = hash_password(password)
            print(f"New Hash for '{password}': {new_hash}")
            print("If the new hash works, we should update the DB.")

            # Auto-fix
            doctor.password_hash = new_hash
            db.session.commit()
            print("✅ Database updated with new valid hash. Try logging in now.")

if __name__ == "__main__":
    debug_auth()

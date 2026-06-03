
import sys
import os

sys.path.append(os.getcwd())

from web.backend.app import create_app, db

def clean_db():
    app = create_app()
    with app.app_context():
        print(f"DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        try:
            db.drop_all()
            print("✅ All tables dropped. Database is clean.")
        except Exception as e:
            print(f"❌ Error dropping tables: {e}")

if __name__ == "__main__":
    clean_db()

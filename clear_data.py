from main import app, db  # Import app and db directly if create_app does not exist
from main import Employer, Info, Application  # Import your models

def clear_all_data():
    try:
        # Delete data from each table
        db.session.query(Employer).delete()
        db.session.query(Info).delete()
        db.session.query(Application).delete()
        
        # Commit the changes to the database
        db.session.commit()
        print("Data cleared from all tables successfully.")

    except Exception as e:
        db.session.rollback()  # Rollback if there is an error
        print("An error occurred:", e)

# Use the application context
with app.app_context():
    clear_all_data()

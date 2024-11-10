from main import app, db, Info, Application 

with app.app_context():
    # Clear all data in the tables
    db.session.query(Info).delete()
    db.session.query(Application).delete()
    db.session.commit()

    print("Data cleared from Info and Application tables!")

from app import create_app, db

app = create_app()

with app.app_context():
    print(f"Database URL: {db.engine.url}")
    print("\nDatabase schema:")
    print("----------------")
    
    # Get table info
    result = db.engine.execute(".schema clients").fetchall()
    for row in result:
        print(row)
    
    print("\nColumns in clients table:")
    print("----------------------")
    result = db.engine.execute("PRAGMA table_info(clients)").fetchall()
    for row in result:
        print(f"{row[1]}: {row[2]} (default: {row[4]})")

from database import Base, engine, init_db, get_db_info

def create_tables():
    print("Connecting to database...")
    info = get_db_info()
    print(f"Active DB Engine: {info['engine']} (alive: {info['is_alive']}, name: {info['db_name']})")
    
    init_db()
    print("Database tables created and initialized successfully!")
    print("Registered tables:", list(Base.metadata.tables.keys()))


if __name__ == "__main__":
    create_tables()

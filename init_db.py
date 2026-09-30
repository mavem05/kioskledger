from database import engine, Base
import models

print("Creating tables in Supabase...")
Base.metadata.create_all(bind=engine)
print("Database schema successfully generated!")
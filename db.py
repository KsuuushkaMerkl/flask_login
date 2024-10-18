from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://user:pass@postgres:5432/db')

Session = sessionmaker(bind=engine)

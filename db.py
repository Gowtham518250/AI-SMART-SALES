from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL
#from urlib.parse import quote_plus
load_dotenv()
host="localhost"
password="Gowtham@2004"
print("port",os.getenv("port"))
print("Host",os.getenv("host"))
print("Password",os.getenv("password"))
#encoded_password=quote_plus(password)
db_url=URL.create("postgresql+psycopg2",username="postgres",
                   password=password,
                   host=host,
        port=5432,
    database="Data_Analytics")
engine = create_engine(
    db_url,
    future=True,
    implicit_returning=False
)
sessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()
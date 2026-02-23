from fastapi import FastAPI,HTTPException,Depends,Form,APIRouter, Header
from RAG_APP import db
from RAG_APP.db import engine,sessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from RAG_APP.db import Base
from RAG_APP.authentication import hash_password,verify_password
from pydantic import BaseModel,EmailStr,Field,field_validator
from sqlalchemy import (Column, Integer, String, Numeric, Date, DateTime,
    ForeignKey, CheckConstraint, Computed)
from datetime import date,datetime
from sqlalchemy.sql import func
import secrets
with engine.connect():
    print("Engine connected")
class User(Base):
    __tablename__ = "user_details"

    id = Column(Integer, primary_key=True,nullable=False)
    user_name = Column(String(100),nullable=False)
    email = Column(String(100), unique=True,nullable=False)
    password = Column(String(100),nullable=False)
class sales(Base):
    __tablename__="sales"
    id=Column(Integer,primary_key=True)
    shopkeeper_id = Column(
        Integer,
        ForeignKey("user_details.id", ondelete="CASCADE"),
        nullable=False
    )
    product_name=Column(String(100),nullable=False)
    price=Column(Numeric(10,2),nullable=False)
    quantity=Column(Integer,CheckConstraint("quantity>0"),nullable=False)
    total=Column(Numeric(10, 2), nullable=False)
    sale_date=Column(Date)
    created_at=Column(DateTime)
def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()
class UserCreate(BaseModel):
    user_name: str= Field(...,min_length=3,max_length=50)
    email: EmailStr
    password:str= Field(...,min_length=6)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(c.isalpha() for c in v):
            raise ValueError('Password must contain letters')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain numbers')
        return v
class Token(Base):
    __tablename__="tokens"
    id=Column(Integer,primary_key=True)
    token=Column(String(64),unique=True,nullable=False)
    user_id=Column(Integer,ForeignKey("user_details.id",ondelete="CASCADE"),nullable=False)
    created_at = Column(DateTime)
router=APIRouter()
@router.post("/register")
def register_user(user:UserCreate,db:Session=Depends(get_db)):
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered. Please login or use a different email.")
        
        password = hash_password(user.password)
        print("Hashed Password:", password)
        
        new_user = User(
            user_name=user.user_name,
            email=user.email,
            password=password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully", "user_id": new_user.id}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
@router.post("/login")
def login_user(email:str=Form(...),password:str=Form(...),db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==email).first()
    if not user:
        raise HTTPException(status_code=400,detail="Email not found. Please register first.")
    if not verify_password(password,user.password):
        raise HTTPException(status_code=400,detail="Incorrect password")
    token=secrets.token_hex(32)
    new_token=(Token(
    token=token,
    user_id=user.id,
    created_at=datetime.utcnow()
))
    db.add(new_token)   
    db.commit()
    #db.refresh(user)
    return {"message":"Login successful","user_id":user.id,"token":token}
async def check_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> int:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.replace("Bearer ", "")

    token_entry = db.query(Token).filter(Token.token == token).first()
    if not token_entry:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return token_entry.user_id
@router.post("/sales")
async def selled_items(product:str=Form(...),price:float=Form(...),quantity:int=Form(...),user_id:int=Depends(check_current_user),db:Session=Depends(get_db)):
    shopkeeper_shales=sales(
        shopkeeper_id=user_id,
        product_name=product,
        price=price,
        quantity=quantity,
        total=price*quantity,
        sale_date=date.today(),
        created_at=datetime.utcnow()
    )
    db.add(shopkeeper_shales)
    db.commit()
    return {"message":"Sale recorded successfully"}


@router.get('/sales')
async def get_sales(user_id:int=Depends(check_current_user), db: Session = Depends(get_db)):
    rows = db.query(sales).filter(sales.shopkeeper_id == user_id).order_by(sales.created_at.desc()).all()
    result = []
    for r in rows:
        result.append({
            'product': r.product_name,
            'price': float(r.price),
            'quantity': r.quantity,
            'total': float(r.total),
            'sale_date': r.sale_date.isoformat() if r.sale_date else None,
            'created_at': r.created_at.isoformat() if r.created_at else None,
        })
    return result
Base.metadata.create_all(bind=engine)
def get_user_sales(user_id:int=Depends(check_current_user),db:Session=Depends(get_db)):
    print(type(db))
    date_today=date.today()
    user_data=db.query(sales).filter(sales.shopkeeper_id==user_id,sales.sale_date==date_today).all()
    return user_data




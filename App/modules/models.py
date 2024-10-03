from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, validates
from datetime import datetime
import enum
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

Base = declarative_base()

class UserType(enum.Enum):
    customer = "customer"
    admin = "admin"

class OrderStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    completed = "completed"
    cancelled = "cancelled"

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    type = Column(Enum(UserType), nullable=False)
    address = Column(String)
    phone_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    welcome_email_sent = Column(Boolean, default=False)
    cookie_policy_accepted = Column(Boolean, default=False)
    orders = relationship("Order", back_populates="user")
    

    @validates('email')
    def validate_email(self, key, address):
        assert '@' in address
        return address

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False, default=1)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    delivery_address = Column(String, nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending)
    total_price = Column(Float, nullable=False)
    payment_status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    transaction_id = Column(String, nullable=True)
    user = relationship("User", back_populates="orders")
    product = relationship("Product")

    def calculate_total_price(self):
        return self.quantity * self.product.price

class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    plan_name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    user = relationship("User")

class PaymentTransaction(Base):
    __tablename__ = 'payment_transactions'
    id = Column(Integer, primary_key=True)
    order_id = Column(String, ForeignKey('orders.id'))
    amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)
    payment_method = Column(String)
    order = relationship("Order")

def setup_database(database_url):
    engine = create_engine(database_url, echo=True)
    
    # Create all tables if they don't exist
    Base.metadata.create_all(engine)
    
    return sessionmaker(bind=engine)

# Load the DATABASE_URL from the environment variables
database_url = os.getenv("DATABASE_URL")
SessionLocal = setup_database(database_url)

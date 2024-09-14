from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# ... (keep the existing imports and Base declaration)

class Order(Base):
  __tablename__ = 'orders'
  id = Column(String, primary_key=True)     # Unique identifier for the order
  user_id = Column(String, ForeignKey('users.id'))  # Foreign key to the User table
  product_id = Column(Integer, ForeignKey('products.id'))  # Foreign key to the Product table
  date = Column(DateTime, nullable=False)    # Order date
  delivery_address = Column(String, nullable=False)  # Delivery address for the order
  status = Column(String, nullable=False)     # Order status (e.g., Pending, Completed)
  start_date = Column(Date)  # New field: Start date for the order
  delivery_time_preference = Column(String)  # New field: Delivery time preference
  product = relationship("Product")          # Relationship to the Product model

# ... (keep the rest of the file as is)

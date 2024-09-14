# models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Define the base class for declarative models
Base = declarative_base()

# Define the User model
class User(Base):
  __tablename__ = 'users'
  id = Column(String, primary_key=True)  # Unique identifier for the user
  name = Column(String, nullable=False)   # User's name
  email = Column(String, unique=True, nullable=False)  # User's email (must be unique)
  type = Column(String, nullable=False)    # User type (e.g., customer, admin)
  address = Column(String)                  # User's address

# Define the Product model
class Product(Base):
  __tablename__ = 'products'
  id = Column(Integer, primary_key=True)   # Unique identifier for the product
  name = Column(String, nullable=False)      # Product name
  description = Column(String)               # Product description
  price = Column(Float, nullable=False)      # Product price

# Define the Order model
class Order(Base):
  __tablename__ = 'orders'
  id = Column(String, primary_key=True)     # Unique identifier for the order
  user_id = Column(String, ForeignKey('users.id'))  # Foreign key to the User table
  product_id = Column(Integer, ForeignKey('products.id'))  # Foreign key to the Product table
  date = Column(DateTime, nullable=False)    # Order date
  delivery_address = Column(String, nullable=False)  # Delivery address for the order
  status = Column(String, nullable=False)     # Order status (e.g., Pending, Completed)
  user = relationship("User")                # Relationship to the User model
  product = relationship("Product")          # Relationship to the Product model

# Function to set up the database
def setup_database(database_url):
  engine = create_engine(database_url, echo=True)  # Create the database engine
  Base.metadata.create_all(engine)                  # Create all tables in the database
  return sessionmaker(bind=engine)                   # Return a session factory

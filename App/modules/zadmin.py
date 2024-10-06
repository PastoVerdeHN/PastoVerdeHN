import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import func
from datetime import datetime, timedelta
from contextlib import contextmanager
from .models import SessionLocal

st.set_page_config(page_title="E-commerce Dashboard", page_icon="🛍️", layout="wide")

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import your database models and setup
from .models import User, Product, Order, Subscription, PaymentTransaction, UserType, SessionLocal
# Set page config
st.set_page_config(page_title="E-commerce Dashboard", page_icon="🛍️", layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Users", "Products", "Orders", "Subscriptions", "Analytics"])

# Database session
session = SessionLocal()

def overview_page():
    with get_db() as session:
        st.title("E-commerce Dashboard Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_users = session.query(func.count(User.id)).scalar()
            st.metric("Total Users", total_users)
        
        with col2:
            total_products = session.query(func.count(Product.id)).scalar()
            st.metric("Total Products", total_products)
        
        with col3:
            total_orders = session.query(func.count(Order.id)).scalar()
            st.metric("Total Orders", total_orders)
        
        with col4:
            total_revenue = session.query(func.sum(Order.total_price)).scalar()
            st.metric("Total Revenue", f"${total_revenue:.2f}")
        
        # Recent Orders
        recent_orders = session.query(Order).order_by(Order.created_at.desc()).limit(5).all()
        if recent_orders:
            order_data = [{
                "ID": order.id,
                "User": order.user.name if order.user else "N/A",
                "Product": order.product.name if order.product else "N/A",
                "Status": order.status.value if order.status else "N/A",
                "Total": f"${order.total_price:.2f}" if order.total_price else "N/A"
            } for order in recent_orders]
            st.table(pd.DataFrame(order_data))
        else:
            st.info("No recent orders found.")


def users_page():
    st.title("User Management")
    
    # User creation form
    with st.expander("Create New User"):
        with st.form("new_user_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            user_type = st.selectbox("User Type", [type.value for type in UserType])
            address = st.text_input("Address")
            phone_number = st.text_input("Phone Number")
            
            if st.form_submit_button("Create User"):
                new_user = User(
                    id=f"user_{datetime.now().timestamp()}",
                    name=name,
                    email=email,
                    type=UserType(user_type),
                    address=address,
                    phone_number=phone_number
                )
                session.add(new_user)
                session.commit()
                st.success("User created successfully!")
    
    # User list
    st.subheader("User List")
    users = session.query(User).all()
    user_data = [{"ID": user.id, "Name": user.name, "Email": user.email, "Type": user.type.value, "Active": user.is_active} for user in users]
    st.dataframe(pd.DataFrame(user_data))

def products_page():
    st.title("Product Management")
    
    # Product creation form
    with st.expander("Add New Product"):
        with st.form("new_product_form"):
            name = st.text_input("Product Name")
            description = st.text_area("Description")
            price = st.number_input("Price", min_value=0.0, step=0.01)
            stock = st.number_input("Stock", min_value=0, step=1)
            category = st.text_input("Category")
            
            if st.form_submit_button("Add Product"):
                new_product = Product(
                    name=name,
                    description=description,
                    price=price,
                    stock=stock,
                    category=category
                )
                session.add(new_product)
                session.commit()
                st.success("Product added successfully!")
    
    # Product list
    st.subheader("Product List")
    products = session.query(Product).all()
    product_data = [{"ID": product.id, "Name": product.name, "Price": f"${product.price:.2f}", "Stock": product.stock, "Category": product.category} for product in products]
    st.dataframe(pd.DataFrame(product_data))

def orders_page():
    with get_db() as session:
    st.title("Order Management")
    
    # Order creation form
    with st.expander("Create New Order"):
        with st.form("new_order_form"):
            user = st.selectbox("User", [user.name for user in session.query(User).all()])
            product = st.selectbox("Product", [product.name for product in session.query(Product).all()])
            quantity = st.number_input("Quantity", min_value=1, step=1)
            delivery_address = st.text_input("Delivery Address")
            
            if st.form_submit_button("Create Order"):
                user_obj = session.query(User).filter_by(name=user).first()
                product_obj = session.query(Product).filter_by(name=product).first()
                
                new_order = Order(
                    id=f"order_{datetime.now().timestamp()}",
                    user_id=user_obj.id,
                    product_id=product_obj.id,
                    quantity=quantity,
                    delivery_address=delivery_address,
                    total_price=product_obj.price * quantity
                )
                session.add(new_order)
                session.commit()
                st.success("Order created successfully!")
    
    # Order list
    st.subheader("Order List")
    orders = session.query(Order).all()
    order_data = [{
        "ID": order.id,
        "User": order.user.name if order.user else "N/A",
        "Product": order.product.name if order.product else "N/A",
        "Quantity": order.quantity,
        "Total": f"${order.total_price:.2f}" if order.total_price else "N/A",
        "Status": order.status.value if order.status else "N/A"
    } for order in orders]
    st.dataframe(pd.DataFrame(order_data))

def subscriptions_page():
    st.title("Subscription Management")
    
    # Subscription creation form
    with st.expander("Create New Subscription"):
        with st.form("new_subscription_form"):
            user = st.selectbox("User", [user.name for user in session.query(User).all()])
            plan_name = st.text_input("Plan Name")
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            
            if st.form_submit_button("Create Subscription"):
                user_obj = session.query(User).filter_by(name=user).first()
                
                new_subscription = Subscription(
                    user_id=user_obj.id,
                    plan_name=plan_name,
                    start_date=start_date,
                    end_date=end_date
                )
                session.add(new_subscription)
                session.commit()
                st.success("Subscription created successfully!")
    
    # Subscription list
    st.subheader("Subscription List")
    subscriptions = session.query(Subscription).all()
    subscription_data = [{"ID": sub.id, "User": sub.user.name, "Plan": sub.plan_name, "Start Date": sub.start_date, "End Date": sub.end_date, "Active": sub.is_active} for sub in subscriptions]
    st.dataframe(pd.DataFrame(subscription_data))

def analytics_page():
    st.title("Analytics")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Convert dates to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Sales over time
    sales_data = session.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_price).label('total_sales')
    ).filter(Order.created_at.between(start_datetime, end_datetime)
    ).group_by(func.date(Order.created_at)).all()
    
    sales_df = pd.DataFrame(sales_data, columns=['date', 'total_sales'])
    st.subheader("Sales Over Time")
    fig = px.line(sales_df, x='date', y='total_sales', title='Daily Sales')
    st.plotly_chart(fig)
    
    # Top selling products
    top_products = session.query(
        Product.name,
        func.sum(Order.quantity).label('total_quantity'),
        func.sum(Order.total_price).label('total_revenue')
    ).join(Order).filter(Order.created_at.between(start_datetime, end_datetime)
    ).group_by(Product.id).order_by(func.sum(Order.quantity).desc()).limit(10).all()
    
    top_products_df = pd.DataFrame(top_products, columns=['product', 'quantity', 'revenue'])
    st.subheader("Top Selling Products")
    fig = px.bar(top_products_df, x='product', y='quantity', title='Top 10 Selling Products')
    st.plotly_chart(fig)
    
    # User acquisition
    new_users = session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('new_users')
    ).filter(User.created_at.between(start_datetime, end_datetime)
    ).group_by(func.date(User.created_at)).all()
    
    new_users_df = pd.DataFrame(new_users, columns=['date', 'new_users'])
    st.subheader("User Acquisition")
    fig = px.bar(new_users_df, x='date', y='new_users', title='New Users per Day')
    st.plotly_chart(fig)

# Main app logic
if page == "Overview":
    overview_page()
elif page == "Users":
    users_page()
elif page == "Products":
    products_page()
elif page == "Orders":
    orders_page()
elif page == "Subscriptions":
    subscriptions_page()
elif page == "Analytics":
    analytics_page()

# Close the database session
session.close()

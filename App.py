import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import random
from sqlalchemy  import create_engine, Column, Integer, String, DateTime,ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import sqlalchemy import Float
from auth0_component import login_button
import os
from dotenv import load_dotenv

# Configuración de la página
st.set_page_config(
    page_title="Pasto Verde",
    page_icon="🌿",
    layout="wide"
)

# Aplicar tema de color
COLOR_PRIMARIO = "#4CAF50"
COLOR_SECUNDARIO = "#8BC34A"
COLOR_FONDO = "#E8F5E9"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {COLOR_FONDO};
    }}
    .stButton>button {{
        background-color: {COLOR_PRIMARIO};
        color: white;
    }}
    .stTextInput>div>div>input {{
        background-color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

# Título principal
st.title("🌿 Pasto Verde")
st.sidebar.success("Seleccione una página arriba.")

# Cargar variables de entorno
load_dotenv()
AUTH0_CLIENT_ID = st.secrets["auth0"]["AUTH0_CLIENT_ID"]
AUTH0_DOMAIN = st.secrets["auth0"]["AUTH0_DOMAIN"]
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")

# Configuración de SQLAlchemy
Base = sqlalchemy.orm.declarative_base()
engine = create_engine(st.secrets["database"]["url"], echo=True)
Session = sessionmaker(bind=engine)

# Modelos de SQLAlchemy
class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    direccion = Column(String)

class Producto(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    precio = Column(Float, nullable=False)
    url_imagen = Column(String)

class Suscripcion(Base):
    __tablename__ = 'suscripciones'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(String, ForeignKey('usuarios.id'))
    producto_id = Column(Integer, ForeignKey('productos.id'))
    plan = Column(String, nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime)
    estado = Column(String, nullable=False)
    usuario = relationship("Usuario")
    producto = relationship("Producto")

class Pedido(Base):
    __tablename__ = 'pedidos'
    id = Column(String, primary_key=True)
    usuario_id = Column(String, ForeignKey('usuarios.id'))
    producto_id = Column(Integer, ForeignKey('productos.id'))
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, nullable=False)
    estado = Column(String, nullable=False)
    personalizacion = Column(String)
    usuario = relationship("Usuario")
    producto = relationship("Producto")

Base.metadata.create_all(engine, checkfirst=True)
print("Tablas de base de datos creadas con éxito (o ya existen).")

# Funciones auxiliares
def generar_id_pedido():
    return f"PED-{random.randint(10000, 99999)}"

# Función de autenticación
def autenticacion_auth0():
    if 'usuario' not in st.session_state:
        st.session_state.usuario = None
    
    if st.session_state.usuario is None:
        opcion_auth = st.sidebar.radio("Elija una acción", ["🔑 Iniciar sesión", "📄 Términos y Condiciones"])
        if opcion_auth == "🔑 Iniciar sesión":
            info_usuario = login_button(AUTH0_CLIENT_ID, domain=AUTH0_DOMAIN)
            if info_usuario:
                session = Session()
                usuario = session.query(Usuario).filter_by(email=info_usuario['email']).first()
                if not usuario:
                    usuario = Usuario(
                        id=info_usuario['sub'],
                        nombre=info_usuario['name'],
                        email=info_usuario['email'],
                        direccion=''
                    )
                    session.add(usuario)
                    session.commit()
                st.session_state.usuario = usuario
                st.success(f"¡Bienvenido, {usuario.nombre}!")
                st.experimental_rerun()
    return st.session_state.usuario

# Función principal
def main():
    usuario = autenticacion_auth0()
    if usuario:
        if 'pagina_actual' not in st.session_state:
            st.session_state.pagina_actual = "🏠 Inicio"
        
        # Elementos del menú
        elementos_menu = [
            "🏠 Inicio",
            "🌱 Productos",
            "🔄 Suscripciones",
            "🛒 Pedidos",
            "👤 Perfil",
            "📞 Soporte"
        ]
        
        st.sidebar.title("Menú")
        seleccion = st.sidebar.radio("Ir a", elementos_menu)
        
        if seleccion == "🏠 Inicio":
            st.header("Bienvenido a Pasto Verde")
            st.write("¡Descubre nuestros productos de pasto premium y ecológico para mascotas!")
        
        elif seleccion == "🌱 Productos":
            st.header("Nuestros Productos")
            # Añadir lógica de listado de productos y pedidos aquí
        
        elif seleccion == "🔄 Suscripciones":
            st.header("Gestiona Tus Suscripciones")
            # Añadir lógica de gestión de suscripciones aquí
        
        elif seleccion == "🛒 Pedidos":
            st.header("Tus Pedidos")
            # Añadir historial de pedidos y lógica de seguimiento aquí
        
        elif seleccion == "👤 Perfil":
            st.header("Tu Perfil")
            # Añadir gestión de perfil de usuario aquí
        
        elif seleccion == "📞 Soporte":
            st.header("Soporte al Cliente")
            # Añadir características de soporte, FAQ e información de contacto aquí

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import time
from datetime import datetime
import google.generativeai as genai
from PIL import Image
import io
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Pandas Salvajes Football Team",
    page_icon="🐼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS PERSONALIZADOS (AÑO NUEVO) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    
    /* Texto del menú lateral en Blanco */
    section[data-testid="stSidebar"] {
        background-color: #000000;
    }
    section[data-testid="stSidebar"] .stText, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] .stRadio > label {
        color: #FFFFFF !important;
        font-weight: 500;
    }

    /* Animación de la Mascota (Flotado y Pulso) */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
        100% { transform: translateY(0px); }
    }
    .animated-panda {
        display: inline-block;
        animation: float 3s ease-in-out infinite;
        transition: all 0.5s ease-in-out;
    }

    /* Estilo General Naranja y Negro */
    .stButton>button {
        background-color: #FF6600;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #e65c00;
        border: 1px solid white;
        color: white;
    }
    
    .card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-top: 5px solid #FF6600;
    }
    
    .panda-container {
        text-align: center;
        background: linear-gradient(135deg, #111111 0%, #222222 100%);
        color: white;
        padding: 40px;
        border-radius: 25px;
        border: 2px solid #FF6600;
        overflow: hidden;
    }
    
    h1, h2, h3 { color: #1a1a1a; font-family: 'Impact', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A DATOS ---
def load_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read()
        return df
    except Exception:
        data = {
            'usuario': ['jugadora1', 'jugadora2', 'admin'],
            'password': ['1234', '5678', 'admin'],
            'nombre': ['Ana García', 'Sofía López', 'Coach Principal'],
            'player_id': ['PANDA01', 'PANDA02', 'ADMIN'],
            '40yds': ['4.8s', '5.1s', '-'],
            'vertical': ['25in', '22in', '-'],
            'pagos_deuda': [500, 1200, 0],
            'multas': [100, 50, 0]
        }
        return pd.DataFrame(data)

# --- INICIALIZACIÓN DE ESTADO ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'panda_stats' not in st.session_state:
    st.session_state.panda_stats = {"nivel": 1.0, "salud": 100, "felicidad": 80}
if 'galeria_fotos' not in st.session_state:
    st.session_state.galeria_fotos = []

# --- LOGIN AUTOMÁTICO ---
query_params = st.query_params
if not st.session_state.logged_in and "id" in query_params:
    df = load_data()
    match = df[df['player_id'] == query_params["id"]]
    if not match.empty:
        st.session_state.user_data = match.iloc[0].to_dict()
        st.session_state.logged_in = True
        st.toast(f"🐾 ¡Bienvenida a la manada, {st.session_state.user_data['nombre']}!", icon="🐼")

# --- FUNCIONES IA ---
def consultar_ia(prompt):
    if not st.session_state.get('api_key'):
        return "Configura la API Key en el menú lateral."
    try:
        genai.configure(api_key=st.session_state.api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- VISTAS ---

def login_view():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        # LOGO PRINCIPAL
        st.image("https://img.freepik.com/vector-premium/lindo-panda-jugando-futbol-americano-dibujos-animados-vector-icono-ilustracion-deporte-naturaleza_138676-4740.jpg", width=220)
        st.title("PANDAS SALVAJES")
        st.markdown("### 🏈 Fuerza, Garra y Lealtad")
        
        tab1, tab2 = st.tabs(["Acceso Manual", "Acceso NFC"])
        with tab1:
            user = st.text_input("Usuario")
            pw = st.text_input("Contraseña", type="password")
            if st.button("INICIAR SESIÓN"):
                df = load_data()
                match = df[(df['usuario'] == user) & (df['password'] == pw)]
                if not match.empty:
                    st.session_state.user_data = match.iloc[0].to_dict()
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Acceso denegado.")
        with tab2:
            st.info("Acerca tu tag NFC de Pandas Salvajes.")
            if st.button("Simular Escaneo NFC"):
                st.query_params["id"] = "PANDA01"
                st.rerun()

def home_view():
    user = st.session_state.user_data
    st.title(f"🐾 Perfil Salvaje: {user['nombre']}")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f'''
        <div class="card">
            <h3 style="color:#FF6600; margin-top:0;">Estatus</h3>
            <p><b>ID Manada:</b> {user['player_id']}</p>
            <p><b>Saldo Pendiente:</b> <span style="color:red;">${user['pagos_deuda'] + user['multas']}</span></p>
        </div>
        ''', unsafe_allow_html=True)
        st.metric("Velocidad 40 Yds", user['40yds'])
        st.metric("Salto Vertical", user['vertical'])

    with col2:
        st.subheader("📢 Noticias de la Manada")
        st.image("https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=800")
        st.info("🚨 Notificación: El entrenamiento de mañana se mueve a las 8:00 AM.")

def panda_view():
    st.title("🐼 Centro de Entrenamiento Panda")
    stats = st.session_state.panda_stats
    
    # Lógica de crecimiento visual (Tamaño basado en nivel)
    # Nivel 1 = 100px, Nivel 10 = 250px
    size = min(100 + (stats['nivel'] * 15), 250)
    
    panda_emoji = "🐼"
    if stats['salud'] < 40: panda_emoji = "🤒"
    elif stats['nivel'] >= 5: panda_emoji = "🥋🐼"
    elif stats['nivel'] >= 10: panda_emoji = "🔥🐼🔥"

    st.markdown(f'''
    <div class="panda-container">
        <div class="animated-panda" style="font-size: {size}px;">
            {panda_emoji}
        </div>
        <h2 style="color:#FF6600; margin-top:20px;">Nivel de Evolución: {int(stats['nivel'])}</h2>
        <p style="font-size: 1.2em;">¡Tu Panda está creciendo con tu esfuerzo!</p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.write("---")
    
    # Notificaciones dinámicas de Retos
    st.subheader("🎯 Retos y Recomendaciones")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("💪 Completar sesión de Gimnasio"):
            stats['salud'] = min(100, stats['salud'] + 10)
            stats['nivel'] += 0.5
            st.toast("¡Nivel aumentado! Tu panda es más fuerte.", icon="🏋️")
            st.success("Notificación: Has ganado +0.5 de Nivel Salvaje.")
            
    with col_b:
        if st.button("🥦 Registrar comida saludable"):
            stats['felicidad'] = min(100, stats['felicidad'] + 15)
            stats['nivel'] += 0.2
            st.toast("¡Panda feliz! Salud mejorada.", icon="🍎")
            st.info("Recomendación: Consume proteína en los próximos 30 min.")

def perfil_view():
    st.title("📝 Datos de Jugadora")
    with st.form("perfil"):
        c1, c2 = st.columns(2)
        c1.text_input("Nombre", value=st.session_state.user_data['nombre'])
        c2.date_input("Nacimiento")
        st.file_uploader("Subir Identificación")
        if st.form_submit_button("Guardar"):
            st.toast("Datos actualizados localmente", icon="✅")

def gym_view():
    st.title("🏋️ GYM Salvaje")
    st.number_input("RM Bench Press", 0)
    if st.button("Generar Rutina IA"):
        st.write(consultar_ia("Dame 3 ejercicios clave para potencia en Pandas Salvajes."))

def alimentacion_view():
    st.title("🍎 Nutrición")
    st.camera_input("Foto de tu dieta")
    st.toast("Tip: La hidratación es clave hoy.", icon="💧")

def estudio_view():
    st.title("📖 Playbook")
    st.info("Estrategias próximamente.")

def pagos_view():
    st.title("💰 Pagos")
    st.metric("Total Pendiente", f"${st.session_state.user_data['pagos_deuda']}")

def tienda_view():
    st.title("🛒 Tienda")
    st.write("Jerseys y equipo próximamente.")

def fotos_view():
    st.title("📸 Galería")
    if st.sidebar.checkbox("Subir Fotos"):
        st.file_uploader("Seleccionar", accept_multiple_files=True)

# --- NAVEGACIÓN ---
if st.session_state.logged_in:
    # LOGO EN SIDEBAR
    st.sidebar.image("https://img.freepik.com/vector-premium/lindo-panda-jugando-futbol-americano-dibujos-animados-vector-icono-ilustracion-deporte-naturaleza_138676-4740.jpg", width=120)
    st.sidebar.markdown("<h2 style='color:#FF6600; text-align:center;'>PANDAS SALVAJES</h2>", unsafe_allow_html=True)
    
    page = st.sidebar.radio("IR A:", ["Inicio", "Datos Jugadora", "Mascota Panda", "GYM", "Alimentación", "Estudio", "Pagos", "Tienda", "Fotos"])
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()

    if page == "Inicio": home_view()
    elif page == "Datos Jugadora": perfil_view()
    elif page == "Mascota Panda": panda_view()
    elif page == "GYM": gym_view()
    elif page == "Alimentación": alimentacion_view()
    elif page == "Estudio": estudio_view()
    elif page == "Pagos": pagos_view()
    elif page == "Tienda": tienda_view()
    elif page == "Fotos": fotos_view()
else:
    login_view()

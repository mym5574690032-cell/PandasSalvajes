import streamlit as st
import pandas as pd
import time
from datetime import datetime
import google.generativeai as genai
from PIL import Image
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Pandas Salvajes Football Team",
    page_icon="🐼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS PERSONALIZADOS (IDENTIDAD PANDAS SALVAJES) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    
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
        background: linear-gradient(135deg, #000000 0%, #333333 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #FF6600;
    }
    
    h1, h2, h3 { color: #1a1a1a; font-family: 'Impact', sans-serif; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #000000;
    }
    section[data-testid="stSidebar"] .stRadio > label {
        color: #FF6600 !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOCK DATA ---
def load_mock_data():
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
    st.session_state.panda_stats = {"nivel": 1, "salud": 100, "felicidad": 80, "last_check": datetime.now()}
if 'galeria_fotos' not in st.session_state:
    st.session_state.galeria_fotos = []

# --- LÓGICA DE LOGIN AUTOMÁTICO (NFC URL) ---
query_params = st.query_params
if not st.session_state.logged_in and "id" in query_params:
    df = load_mock_data()
    match = df[df['player_id'] == query_params["id"]]
    if not match.empty:
        st.session_state.user_data = match.iloc[0].to_dict()
        st.session_state.logged_in = True
        st.toast(f"🐾 ¡Bienvenida a la manada, {st.session_state.user_data['nombre']}!")

# --- FUNCIONES DE IA ---
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
        st.image("https://img.freepik.com/vector-premium/lindo-panda-jugando-futbol-americano-dibujos-animados-vector-icono-ilustracion-deporte-naturaleza_138676-4740.jpg", width=200)
        st.title("PANDAS SALVAJES")
        st.markdown("### 🏈 Fuerza, Garra y Lealtad")
        
        tab1, tab2 = st.tabs(["Manual", "NFC Scan"])
        
        with tab1:
            user = st.text_input("Usuario")
            pw = st.text_input("Contraseña", type="password")
            if st.button("INICIAR SESIÓN"):
                df = load_mock_data()
                match = df[(df['usuario'] == user) & (df['password'] == pw)]
                if not match.empty:
                    st.session_state.user_data = match.iloc[0].to_dict()
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Acceso denegado.")

        with tab2:
            st.info("Acerca tu tag NFC de Pandas Salvajes.")
            if st.button("Simular NFC (PANDA01)"):
                st.query_params["id"] = "PANDA01"
                st.rerun()

def home_view():
    user = st.session_state.user_data
    st.title(f"🐾 Perfil Salvaje: {user['nombre']}")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f'''
        <div class="card">
            <h3 style="color:#FF6600; margin-top:0;">Estatus Actual</h3>
            <p><b>ID Manada:</b> {user['player_id']}</p>
            <p><b>Saldo Pendiente:</b> <span style="color:red;">${user['pagos_deuda'] + user['multas']}</span></p>
        </div>
        ''', unsafe_allow_html=True)
        
        st.subheader("📈 Pruebas Combine")
        st.metric("Velocidad 40 Yds", user['40yds'])
        st.metric("Salto Vertical", user['vertical'])

    with col2:
        st.subheader("📢 Noticias de la Manada")
        st.image("https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=800", caption="¡Rumbo al campeonato!")
        st.info("No olvides registrar tus comidas para que tu panda no pierda salud.")

def panda_view():
    st.title("🐼 Mi Panda Salvaje")
    stats = st.session_state.panda_stats
    
    panda_emoji = "🐼"
    if stats['salud'] < 50:
        panda_emoji = "🤒"
        status_text = "Tu panda está débil. ¡Necesita entrenamiento!"
    elif stats['nivel'] > 5:
        panda_emoji = "🐻‍❄️🔥"
        status_text = "¡Tu panda es un Guerrero Salvaje!"
    else:
        status_text = "¡Tu panda está listo para el emparrillado!"

    st.markdown(f'''
    <div class="panda-container">
        <h1 style="font-size: 100px; margin: 0;">{panda_emoji}</h1>
        <h2 style="color:#FF6600;">Nivel Salvaje: {int(stats['nivel'])}</h2>
        <p>{status_text}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    c1.metric("Salud Atleta", f"{int(stats['salud'])}%")
    c2.metric("Felicidad / Racha", f"{int(stats['felicidad'])}%")

    st.divider()
    st.subheader("🚀 Acciones para Evolucionar")
    col_a, col_b = st.columns(2)
    if col_a.button("✅ Asistí a Entrenamiento"):
        stats['salud'] = min(100, stats['salud'] + 15)
        stats['nivel'] += 0.5
        st.balloons()
    if col_b.button("✅ Comida Saludable Registrada"):
        stats['felicidad'] = min(100, stats['felicidad'] + 10)
        st.rerun()

def perfil_view():
    st.title("📝 Registro de Jugadora")
    with st.form("perfil_panda"):
        c1, c2 = st.columns(2)
        c1.text_input("Nombre Completo", value=st.session_state.user_data['nombre'])
        c1.text_input("CURP (Escrito)")
        c2.date_input("Fecha de Nacimiento")
        c2.selectbox("Posición Deseada", ["QB", "RB", "WR", "OL", "DL", "LB", "DB"])
        st.file_uploader("Subir Foto Infantil (Tamaño infantil)")
        if st.form_submit_button("Actualizar Manada"):
            st.success("Datos actualizados correctamente.")

def gym_view():
    st.title("🏋️ Gimnasio Salvaje")
    st.subheader("Bitácora de hoy")
    
    col_x, col_y = st.columns(2)
    with col_x:
        st.number_input("Peso Máximo Hoy (lbs)", 0)
        st.number_input("Repeticiones", 0)
    with col_y:
        st.selectbox("Objetivo", ["Bajar de peso", "Subir masa muscular"])
        st.multiselect("Días disponibles", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"])

    if st.button("Consultar IA para Rutina"):
        res = consultar_ia("Dame una rutina de fuerza específica para una jugadora de futbol americano.")
        st.write(res)

def alimentacion_view():
    st.title("🍎 Nutrición y Calorías")
    st.write("Registra tus comidas y recibe consejos de nutrición basados en tu perfil.")
    
    col_cam, col_info = st.columns(2)
    with col_cam:
        st.camera_input("Foto de tu comida para análisis IA")
    with col_info:
        st.metric("Agua Recomendada", "2.5L")
        st.info("Un Panda Salvaje bien alimentado rinde mejor en el campo.")

def estudio_view():
    st.title("📖 Playbook de Jugadas")
    st.warning("⚠️ Esta sección está en construcción por los coaches. Próximamente videos y análisis de rivales.")

def pagos_view():
    st.title("💰 Control de Pagos y Multas")
    u = st.session_state.user_data
    st.metric("Cuota Temporada", f"${u['pagos_deuda']}")
    st.metric("Multas (Retardos/Faltas)", f"${u['multas']}")
    st.button("Informar Pago Realizado")

def tienda_view():
    st.title("🛒 Tienda Pandas Salvajes")
    st.info("🛍️ La tienda oficial estará disponible pronto. Prepárate para el nuevo Jersey.")

def fotos_view():
    st.title("📸 Galería Pandas Salvajes")
    if st.sidebar.checkbox("Subir fotos (Coach)"):
        ups = st.file_uploader("Subir archivos", accept_multiple_files=True)
        if st.button("Publicar Fotos"):
            for f in ups:
                st.session_state.galeria_fotos.append(f)
            st.success("Fotos publicadas en la galería.")
    
    if st.session_state.galeria_fotos:
        cols = st.columns(3)
        for i, f in enumerate(st.session_state.galeria_fotos):
            cols[i%3].image(f, use_container_width=True)
    else:
        st.write("Aún no hay fotos nuevas hoy. ¡Sé la primera en capturar el momento!")

# --- NAVEGACIÓN ---
if st.session_state.logged_in:
    st.sidebar.title("🐾 PANDAS SALVAJES")
    page = st.sidebar.radio("Navegación:", ["Inicio", "Datos Jugadora", "Mascota Panda", "GYM", "Alimentación", "Estudio", "Pagos", "Tienda", "Fotos"])
    
    with st.sidebar.expander("⚙️ Ajustes"):
        st.session_state.api_key = st.text_input("Gemini API Key", type="password")

    if st.sidebar.button("Cerrar Campo"):
        st.session_state.logged_in = False
        st.query_params.clear()
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
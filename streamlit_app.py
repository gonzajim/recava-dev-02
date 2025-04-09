import streamlit as st
from openai import OpenAI
import os

# --- 1. Frontend con Streamlit ---

st.title("Asistente Legal con OpenAI")

# Inicialización de variables de sesión
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'retrieved_evidence' not in st.session_state:
    st.session_state['retrieved_evidence'] = []
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None

# Área de chat
user_query = st.text_input("Pregunta al asistente legal:")

# Sección para mostrar las evidencias recuperadas (se llenará con la respuesta del asistente)
st.subheader("Respuesta del Asistente")
if st.session_state['retrieved_evidence']:
    st.markdown(st.session_state['retrieved_evidence'])
else:
    st.info("La respuesta del asistente aparecerá aquí.")

# Área para mostrar el historial del chat
st.subheader("Historial del Chat")
for message in st.session_state['chat_history']:
    if "user" in message:
        st.markdown(f"**Usuario:** {message['user']}")
    elif "assistant" in message:
        st.markdown(f"**Asistente:** {message['assistant']}")

# --- 2. Configuración del Asistente de OpenAI ---

# *** Reemplaza con el ID de tu asistente creado en OpenAI ***
ASSISTANT_ID = "asst_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Inicializar el cliente de OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- 3. Funciones para interactuar con el Asistente ---

def create_thread():
    """Crea un nuevo hilo para la conversación."""
    thread = client.beta.threads.create()
    st.session_state['thread_id'] = thread.id
    print(f"Hilo creado con ID: {st.session_state['thread_id']}")
    return thread.id

def add_message_to_thread(thread_id, role, content):
    """Añade un mensaje al hilo."""
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role=role,
        content=content,
    )

def run_assistant(thread_id, assistant_id):
    """Ejecuta el asistente en el hilo."""
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    return run.id

def get_run_status(thread_id, run_id):
    """Obtiene el estado de la ejecución del asistente."""
    return client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

def get_assistant_response(thread_id):
    """Obtiene los mensajes del asistente del hilo."""
    messages = client.beta.threads.messages.list(thread_id=thread_id, order="asc")
    assistant_response = ""
    for message in messages.data:
        if message.role == "assistant":
            for content in message.content:
                if content.type == "text":
                    assistant_response += content.text.value + "\n"
    return assistant_response.strip()

# --- 4. Flujo de Procesamiento con el Asistente ---

if st.button("Enviar Pregunta") and user_query:
    st.session_state['retrieved_evidence'] = ""  # Limpiar la sección de evidencias

    if not st.session_state['thread_id']:
        st.session_state['thread_id'] = create_thread()

    add_message_to_thread(st.session_state['thread_id'], "user", user_query)
    st.session_state['chat_history'].append({"user": user_query})

    with st.spinner("Consultando al asistente..."):
        run_id = run_assistant(st.session_state['thread_id'], ASSISTANT_ID)
        while True:
            run_status = get_run_status(st.session_state['thread_id'], run_id)
            print(f"Estado de la ejecución: {run_status.status}")
            if run_status.status == "completed":
                assistant_response = get_assistant_response(st.session_state['thread_id'])
                st.session_state['chat_history'].append({"assistant": assistant_response})
                st.session_state['retrieved_evidence'] = assistant_response
                break
            elif run_status.status in ["queued", "in_progress"]:
                import time
                time.sleep(1)
            else:
                st.error(f"Error al ejecutar el asistente: {run_status.status}")
                break

import streamlit as st
from openai import OpenAI
import os

# --- Configuración de la Página ---
st.set_page_config(layout="wide")

# --- Inicialización de Variables de Sesión ---
if 'audit_history' not in st.session_state:
    st.session_state['audit_history'] = []
if 'assistant_responses' not in st.session_state:
    st.session_state['assistant_responses'] = []
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None

# --- Configuración del Asistente de OpenAI ---
ASSISTANT_ID = "asst_9kfpSYaEJLSDcPlb1f9nt9MF"  # *** REEMPLAZA CON TU ID ***
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- Funciones de Interacción con el Asistente ---
def create_thread():
    thread = client.beta.threads.create()
    st.session_state['thread_id'] = thread.id
    print(f"Hilo creado con ID: {st.session_state['thread_id']}")
    return thread.id

def add_message_to_thread(thread_id, role, content):
    client.beta.threads.messages.create(thread_id=thread_id, role=role, content=content)

def run_assistant(thread_id, assistant_id):
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
    return run.id

def get_run_status(thread_id, run_id):
    return client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

def get_assistant_response(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id, order="asc")
    assistant_response = ""
    for message in messages.data:
        if message.role == "assistant":
            for content in message.content:
                if content.type == "text":
                    assistant_response += content.text.value + "\n"
    return assistant_response.strip()

# --- Layout de la Pantalla ---
left_column, right_column = st.columns(2)

# --- Columna Izquierda: Histórico de Preguntas ---
with left_column:
    st.subheader("Histórico de Preguntas de la Auditoría")
    if st.session_state['audit_history']:
        for i, question in enumerate(st.session_state['audit_history']):
            st.markdown(f"**Pregunta {i+1}:** {question}")
    else:
        st.info("No hay preguntas en el historial.")

# --- Columna Derecha: Interacción y Respuestas ---
with right_column:
    st.subheader("Pregunta y Respuestas")

    # Campo para la nueva pregunta
    user_query = st.text_input("Introduce tu pregunta:")

    # Botón para enviar la pregunta
    if st.button("Enviar Pregunta") and user_query:
        st.session_state['audit_history'].append(user_query)

        if not st.session_state['thread_id']:
            st.session_state['thread_id'] = create_thread()

        add_message_to_thread(st.session_state['thread_id'], "user", user_query)

        with st.spinner("Consultando al asistente..."):
            run_id = run_assistant(st.session_state['thread_id'], ASSISTANT_ID)
            while True:
                run_status = get_run_status(st.session_state['thread_id'], run_id)
                print(f"Estado de la ejecución: {run_status.status}")
                if run_status.status == "completed":
                    assistant_response = get_assistant_response(st.session_state['thread_id'])
                    st.session_state['assistant_responses'].insert(0, assistant_response) # Añadir al principio de la lista
                    break
                elif run_status.status in ["queued", "in_progress"]:
                    import time
                    time.sleep(1)
                else:
                    st.error(f"Error al ejecutar el asistente: {run_status.status}")
                    break

    # Pila de respuestas anteriores (encima del campo de entrada)
    st.subheader("Respuestas Anteriores")
    if st.session_state['assistant_responses']:
        for response in st.session_state['assistant_responses']:
            st.info(response)
    else:
        st.info("Las respuestas del asistente aparecerán aquí.")

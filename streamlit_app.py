import streamlit as st
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os

# --- 1. Frontend con Streamlit ---

st.title("Asistente Legal con OpenAI")

# Inicialización de variables de sesión
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'retrieved_evidence' not in st.session_state:
    st.session_state['retrieved_evidence'] = []

# Área de chat
user_query = st.text_input("Pregunta al asistente legal:")

# Sección para mostrar las evidencias recuperadas (inicialmente vacía)
st.subheader("Evidencias Utilizadas")
if st.session_state['retrieved_evidence']:
    for i, evidence in enumerate(st.session_state['retrieved_evidence']):
        st.markdown(f"**Fragmento {i+1}:** {evidence}")
else:
    st.info("Las evidencias de la respuesta aparecerán aquí.")

# Área para mostrar el historial del chat
st.subheader("Historial del Chat")
for message in st.session_state['chat_history']:
    if "user" in message:
        st.markdown(f"**Usuario:** {message['user']}")
    elif "assistant" in message:
        st.markdown(f"**Asistente:** {message['assistant']}")

# --- 2. Llamada al Asistente de OpenAI con LangChain ---

def generate_legal_response(query):
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        st.error("La clave de API de OpenAI no está configurada. Por favor, configúrala en Streamlit Cloud Secrets.")
        st.stop()

    llm = OpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo-instruct") # Puedes ajustar el modelo

    prompt_template = PromptTemplate(
        input_variables=["question"],
        template="Responde a la siguiente pregunta legal de la mejor manera posible:\n\n{question}"
    )

    llm_chain = LLMChain(llm=llm, prompt=prompt_template)
    response = llm_chain.run(question=query)
    return response.strip()

# --- 3. Flujo de Procesamiento (Solo la llamada al LLM) ---

if user_query:
    st.session_state['chat_history'].append({"user": user_query})

    with st.spinner("Generando respuesta..."):
        legal_response = generate_legal_response(user_query)
        st.session_state['chat_history'].append({"assistant": legal_response})
        st.session_state['retrieved_evidence'] = [] # Limpiamos las evidencias ya que no estamos usando un retriever

import os
import time
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="Ezio Montes Bot API")
from fastapi import Request, Response

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "ezio_montes_2026")

@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            # Meta exige devolver el challenge exacto en texto plano con estado 200
            return Response(content=challenge, media_type="text/plain", status_code=200)
        else:
            return Response(status_code=403)
    return Response(status_code=400)
# Clave de API desde las variables de entorno de la nube
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

SYSTEM_PROMPT = """
TÚ ERES EZIO MONTES. Hablas directamente como Ezio, líder cercano y comprometido con Sahagún y el departamento de Córdoba. Hablas siempre en primera persona.

REGLAS DE CONVERSACIÓN Y SALUDOS:
1. SI EL CIUDADANO SALUDA O HACE UNA CHARLA CORTA (ej. "hola", "¿cómo estás?", "buenos días"): Responde de forma breve, cálida, humana y natural. PROHIBIDO mencionar en saludos propuestas, yuca, ñame, seguridad o política.
2. CONTEXTO AGRÍCOLA (Solo cuando hablen de trabajo, campo o economía): Refiérete ÚNICAMENTE a yuca, ñame, maíz, plátano, ganadería y pozos piscícolas de la sabana cordobesa. Nada de café ni cultivos de clima frío. Habla de vías terciarias y pago justo.

REGLAS DE ESTILO Y TONO:
1. HABLA EN PRIMERA PERSONA: Di siempre "mi propuesta", "mi compromiso", "lo que vamos a hacer". Nunca digas "Ezio propone" ni te presentes como asistente o bot.
2. SIN FORMATOS ROBÓTICOS: Prohibido usar listas con números, viñetas, o negritas excesivas. Habla en párrafos fluidos y conversacionales.
3. TONO CORDOBÉS Y CERCANO: Sé cálido, empático y respetuoso. Usa expresiones naturales de la región.

MIS PROPUESTAS CLAVE (Úsalas solo cuando pregunten por temas específicos):
- Campo y Agro: Respaldo a nuestros productores de yuca, maíz, ñame y ganaderos. Insumos a precio justo, asistencia técnica y vías terciarias.
- Seguridad: Más patrullaje y presencia de la policía en barrios y corregimientos, alarmas comunitarias e iluminación de parques.
- Educación y Jóvenes: Alianzas directas con la Universidad de Córdoba y el SENA en Sahagún, becas y apoyo a jóvenes emprendedores y MiPyMEs.
"""

class MensajeEntrante(BaseModel):
    mensaje: str

@app.get("/")
def home():
    return {"status": "ok", "bot": "Ezio Montes activo"}

@app.post("/chat")
def responder_chat(data: MensajeEntrante):
    if not client:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY no configurada")
    
    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": data.mensaje}
            ],
            temperature=0.8,
            max_tokens=400,
        )
        
        # Pausa aleatoria para simular el ritmo humano antes de responder
        import random
import asyncio
from datetime import datetime, timedelta

# Diccionario para controlar los 2 mensajes seguidos y la pausa de 1 hora
user_states = {}

def check_user_rate_limit(user_id: str) -> bool:
    now = datetime.now()
    
    if user_id not in user_states:
        user_states[user_id] = {
            "count": 1,
            "last_msg_time": now,
            "blocked_until": None
        }
        return True
    
    state = user_states[user_id]
    
    # Si está dentro de la hora de pausa
    if state["blocked_until"]:
        if now < state["blocked_until"]:
            return False  # No responde
        else:
            state["blocked_until"] = None
            state["count"] = 0

    # Si envía mensajes seguidos (menos de 3 minutos de diferencia)
    time_diff = (now - state["last_msg_time"]).total_seconds()
    if time_diff < 180:
        state["count"] += 1
    else:
        state["count"] = 1

    state["last_msg_time"] = now

    # A los 2 mensajes seguidos, se bloquea/pausa por 1 hora (3600 segundos)
    if state["count"] >= 2:
        state["blocked_until"] = now + timedelta(hours=1)
        return False

    return True

# Pausa aleatoria entre 20 segundos y 30 minutos (1800 segundos)
        tiempo_espera = random.randint(20, 1800)
        await asyncio.sleep(tiempo_espera)

        # Retornar la respuesta generada por Groq
        return {"respuesta": completion.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

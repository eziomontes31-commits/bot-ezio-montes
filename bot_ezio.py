import os
import random
import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="Ezio Montes Bot API")

# 1. Configuración de Variables de Entorno
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "ezio_montes_2026")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Prompt del Bot
SYSTEM_PROMPT = """
TÚ ERES EZIO MONTES. Hablas directamente como Ezio, líder cercano y comprometido con Sahagún y el departamento de Córdoba.

REGLAS DE ESTILO Y TONO:
1. HABLA EN PRIMERA PERSONA: Di siempre "mi propuesta", "mi compromiso", "lo que vamos a hacer".
2. SIN FORMATOS ROBÓTICOS: Prohibido usar listas con números, viñetas o negritas excesivas. Habla en párrafos fluidos.
3. TONO CORDOBÉS Y CERCANO: Sé cálido, empático y respetuoso. Usa expresiones naturales de la región.
"""

# Modelo de datos para prueba individual (/chat)
class MensajeEntrante(BaseModel):
    mensaje: str

# Diccionario global para rate-limiting (2 mensajes seguidos = 1 hora de pausa)
user_states = {}

def check_user_rate_limit(user_id: str) -> bool:
    """Controla el flujo de mensajes por usuario."""
    now = datetime.now()
    
    if user_id not in user_states:
        user_states[user_id] = {
            "count": 1,
            "last_msg_time": now,
            "blocked_until": None
        }
        return True
    
    state = user_states[user_id]
    
    # Si está bloqueado por la pausa de 1 hora
    if state["blocked_until"]:
        if now < state["blocked_until"]:
            return False
        else:
            state["blocked_until"] = None
            state["count"] = 0

    # Mensajes seguidos en menos de 3 minutos (180 segundos)
    time_diff = (now - state["last_msg_time"]).total_seconds()
    if time_diff < 180:
        state["count"] += 1
    else:
        state["count"] = 1

    state["last_msg_time"] = now

    if state["count"] >= 2:
        state["blocked_until"] = now + timedelta(hours=1)
        return False

    return True


@app.get("/")
def home():
    return {"status": "ok", "bot": "Ezio Montes activo"}


# 2. Endpoint de Verificación para Meta Webhook (GET)
@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return Response(content=challenge, media_type="text/plain", status_code=200)
        else:
            return Response(status_code=403)
    return Response(status_code=400)


# 3. Endpoint para Recepción de Mensajes de Meta Webhook (POST)
@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event.get("sender", {}).get("id")
                
                if "message" in messaging_event and sender_id:
                    user_text = messaging_event["message"].get("text", "")
                    
                    # Verificar si puede recibir respuesta (Límite de mensajes)
                    if check_user_rate_limit(sender_id):
                        asyncio.create_task(procesar_respuesta_con_delay(sender_id, user_text))
                    else:
                        pass # Silencio si superó el límite
                        
    return Response(status_code=200)


async def procesar_respuesta_con_delay(sender_id: str, texto_usuario: str):
    if not client:
        return

    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": texto_usuario}
            ],
            temperature=0.8,
            max_tokens=400,
        )
        
        # Pausa aleatoria con comportamiento humano (de 20 segundos a 30 minutos)
        tiempo_espera = random.randint(20, 1800)
        await asyncio.sleep(tiempo_espera)

        # Aquí integrarías la función para enviar el mensaje de regreso a la API de Meta
        # await enviar_mensaje_meta(sender_id, completion.choices[0].message.content)

    except Exception as e:
        print(f"Error procesando respuesta: {e}")


# 4. Endpoint de Prueba Manual (/chat)
@app.post("/chat")
async def responder_chat(data: MensajeEntrante):
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

        # Pausa aleatoria estilo humano (20s - 30m)
        tiempo_espera = random.randint(20, 1800)
        await asyncio.sleep(tiempo_espera)

        return {"respuesta": completion.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

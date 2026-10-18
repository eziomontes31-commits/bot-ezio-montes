import os
import time
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq

app = FastAPI(title="Ezio Montes Bot API")

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
        time.sleep(random.uniform(2.0, 4.0))
        
        return {"respuesta": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
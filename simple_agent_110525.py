from flask import Flask, request, jsonify, send_from_directory
from crewai import Agent, Task, Crew
import requests
import os
import traceback
from agent_runner import run_agent_analysis  # ⬆️ Nueva importación

# Habilitar carpeta de archivos estáticos
app = Flask(__name__, static_folder='public', static_url_path='')

# Clave de API de OpenAI desde variable de entorno
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("❌ ERROR: OPENAI_API_KEY no está definido en variables de entorno.")

# Ruta principal (sirve index.html desde carpeta public/)
@app.route('/')
def home():
    return app.send_static_file('index.html')

# Ruta de análisis POST
@app.route('/analyze', methods=['POST'])
def analyze():
    print("🔹 POST /analyze recibido")
    data = request.json
    api_url = data.get('api_url')
    print(f"🔍 URL recibida: {api_url}")

    if not api_url:
        return jsonify({"error": "Se requiere una URL de API"}), 400

    try:
        # 1. Obtener datos de la API externa
        print("🌐 Consultando API externa...")
        api_response = requests.get(api_url)
        print(f"📡 Status API externa: {api_response.status_code}")
        if api_response.status_code != 200:
            return jsonify({"error": f"API externa devolvió código {api_response.status_code}"}), 502
        api_data = api_response.json()
        print("✅ Datos obtenidos de la API externa")

        # 2. Ejecutar análisis con plantilla reutilizable
        print("🧠 Ejecutando análisis con agente plantilla...")
        analysis = run_agent_analysis(
            datos=api_data,
            resumen_preprocesado="",
            rol="Analista de datos",
            objetivo="Analizar datos y proporcionar información valiosa",
            backstory="Experto en análisis de datos con años de experiencia",
            prompt_extra="Analiza estos datos y proporciona conclusiones útiles:",
            modelo="gpt-4"
        )

        return jsonify({
            "analysis": analysis,
            "raw_data": api_data
        })

    except Exception as e:
        print("❌ Error durante el análisis:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Arranque local (no se usa en Render, pero útil para pruebas locales)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando servidor Flask en el puerto {port}...")
    app.run(host='0.0.0.0', port=port)


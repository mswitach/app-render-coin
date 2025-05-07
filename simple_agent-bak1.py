from flask import Flask, request, jsonify
from crewai import Agent, Task, Crew
import requests
import os
import traceback

app = Flask(__name__)

# Clave de API de OpenAI desde variable de entorno
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("❌ ERROR: OPENAI_API_KEY no está definido en variables de entorno.")

@app.route('/')
def home():
    return "CrewAI Simple Agent - Funcionando"

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
        api_data = api_response.json()
        print("✅ Datos obtenidos de la API externa")

        # 2. Crear un agente simple con CrewAI
        print("🧠 Creando agente...")
        agent = Agent(
            role="Analista de datos",
            goal="Analizar datos y proporcionar información valiosa",
            backstory="Experto en análisis de datos con años de experiencia",
            verbose=True,
            allow_delegation=False,
            llm_config={
                "api_key": OPENAI_API_KEY,
                "model": "gpt-4"
            }
        )

        # 3. Crear una tarea para el agente
        task_description = f"Analiza estos datos y proporciona conclusiones útiles: {api_data}"
        print("📝 Creando tarea con datos recibidos")
        task = Task(
            description=task_description,
            expected_output="Un análisis conciso de los datos proporcionados",
            agent=agent
        )

        # 4. Crear un equipo con un solo agente
        print("👥 Inicializando crew")
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=2
        )

        # 5. Ejecutar el equipo y obtener resultados
        print("🚀 Ejecutando crew...")
        result = crew.kickoff()
        print("✅ Crew ejecutado correctamente")

        return jsonify({
            "analysis": result,
            "raw_data": api_data
        })

    except Exception as e:
        print("❌ Error durante el análisis:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando servidor Flask en el puerto {port}...")
    app.run(host='0.0.0.0', port=port)


from flask import Flask, request, jsonify, send_from_directory
from crewai import Agent, Task, Crew
import requests
import os
import traceback
from collections import defaultdict
from datetime import datetime
from agent_runner import run_agent_analysis

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
    api_url = data.get("api_url", "")
    print(f"🔍 URL recibida: {api_url}")

    if not api_url:
        return jsonify({"error": "No se recibió una URL válida"}), 400

    try:
        print("🌐 Consultando API externa...")
        api_response = requests.get(api_url)
        print(f"📡 Status API externa: {api_response.status_code}")
        if api_response.status_code != 200:
            return jsonify({"error": f"API externa devolvió código {api_response.status_code}"}), 502
        api_data = api_response.json()
        print("✅ Datos obtenidos de la API externa")

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

# Ruta de proyección de pedidos por cliente
@app.route('/pedidos', methods=['GET'])
def proyectar_pedidos():
    try:
        print("🔄 GET /pedidos recibido")
        url = "https://crono23.herokuapp.com/items"
        print("🌐 Consultando endpoint de pedidos...")
        response = requests.get(url)
        print(f"📡 Status API pedidos: {response.status_code}")
        pedidos = response.json()
        print(f"📦 Total pedidos recibidos: {len(pedidos)}")

        pedidos_filtrados = [p for p in pedidos if p.get("entregado") == "Terminado Normal"]
        print(f"✅ Pedidos con estado 'Terminado Normal': {len(pedidos_filtrados)}")

        historial = defaultdict(lambda: defaultdict(int))
        for p in pedidos_filtrados:
            codigo = p.get("codigo", "Sin código")
            fecha = p.get("fecha_entrega") or p.get("fecha_remito") or p.get("fecha_planificacion")
            if not fecha:
                continue
            try:
                fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
                clave_mes = fecha_dt.strftime("%Y-%m")
                historial[codigo][clave_mes] += 1
            except Exception as fe:
                print(f"⚠️ Fecha inválida para pedido {p.get('id')}: {fecha}")
                continue

        resumen = "Resumen histórico de pedidos por cliente (últimos 9 meses):\n"
        for codigo, meses in historial.items():
            resumen += f"\nCliente {codigo}:\n"
            for mes, cantidad in sorted(meses.items()):
                resumen += f"  {mes}: {cantidad} pedidos\n"

        print("🧠 Ejecutando agente de predicción de demanda...")
        analisis = run_agent_analysis(
            datos=pedidos_filtrados,
            resumen_preprocesado=resumen,
            rol="Analista de demanda",
            objetivo="Proyectar la cantidad de pedidos esperados por cliente para el mes de junio 2025",
            backstory="Especialista en análisis de comportamiento de compra y pronóstico de demanda",
            prompt_extra=(
                "En base al historial de pedidos por cliente de los últimos 9 meses, proyectá la cantidad de pedidos \
                esperados por cliente para el mes de junio 2025. Mostrá el resultado como una lista de clientes y su demanda esperada."
            ),
            modelo="gpt-4"
        )

        print("✅ Análisis completado. Enviando respuesta...")
        return jsonify({
            "proyeccion": analisis,
            "resumen": resumen
        })

    except Exception as e:
        print("❌ Error en /pedidos:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Arranque local (no se usa en Render, pero útil para pruebas locales)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando servidor Flask en el puerto {port}...")
    app.run(host='0.0.0.0', port=port)


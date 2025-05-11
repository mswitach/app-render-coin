from flask import Flask, jsonify, send_from_directory
import requests
import os
import traceback
from openai import OpenAI

# Habilitar carpeta de archivos estáticos
app = Flask(__name__, static_folder='public', static_url_path='')

# Clave API de OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌ ERROR: Falta la clave OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Ruta principal (sirve index.html desde carpeta public/)
@app.route('/')
def home():
    return app.send_static_file('index.html')

# Ruta que cuenta items y genera una breve conclusión con OpenAI
@app.route('/pedidos', methods=['GET'])
def contar_items():
    try:
        print("🔄 GET /pedidos recibido")
        url = "https://crono23.herokuapp.com/items"
        print(f"🌐 Consultando endpoint de items en {url}...")
        response = requests.get(url)
        print(f"📡 Status API: {response.status_code}")
        if response.status_code != 200:
            return jsonify({"error": f"API devolvió código {response.status_code}"}), 502

        items = response.json()
        cantidad_total = len(items)
        print(f"📦 Total de ítems recibidos: {cantidad_total}")

        # Usar OpenAI para una mini conclusión
        prompt = f"Recibimos {cantidad_total} pedidos. ¿Qué podrías decir brevemente sobre ese volumen?"
        print("🧠 Consultando OpenAI...")
        respuesta = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sos un analista logístico conciso."},
                {"role": "user", "content": prompt}
            ]
        )
        conclusion = respuesta.choices[0].message.content

        return jsonify({
            "total_items": cantidad_total,
            "analisis": conclusion
        })

    except Exception as e:
        print("❌ Error en /pedidos:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Arranque local
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando servidor Flask en el puerto {port}...")
    app.run(host='0.0.0.0', port=port)


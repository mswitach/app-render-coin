import requests

# URL de tu aplicación en Render (reemplazar)
RENDER_URL = "https://tu-app.onrender.com"

# URL de una API pública de ejemplo (datos de criptomonedas)
API_URL = "https://api.coincap.io/v2/assets?limit=3"

# Hacer la solicitud
response = requests.post(
    f"{RENDER_URL}/analyze",
    json={"api_url": API_URL}
)

# Mostrar resultados
print(response.json())

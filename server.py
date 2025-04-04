from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Personajes guardados en memoria
characters = {}
API_KEY = "30824df935cb1676a430c3ef49a4379672d9e42a15548d5823d4451ccd0f1d0b"  # reemplazalo con tu key real

@app.route("/create_character/", methods=["POST"])
def create_character():
    name = request.json["name"]
    personality = request.json["personality"]
    universe = request.json.get("universe", "")
    image_url = request.json["image_url"]

    characters[name] = {
        "name": name,
        "personality": personality,
        "universe": universe,
        "image_url": image_url
    }

    return jsonify({"status": "ok", "character": characters[name]})


@socketio.on("connect")
def on_connect():
    print("Cliente conectado")


@socketio.on("disconnect")
def on_disconnect():
    print("Cliente desconectado")


@socketio.on("message")
def handle_message(data):
    char_name = data.get("character")
    user_msg = data.get("message")
    char = characters.get(char_name)

    if not char:
        emit("response", "Personaje no encontrado.")
        return

    prompt = f"""
    Universo: {char['universe']}
    Personaje: {char_name}
    Personalidad: {char['personality']}
    Usuario dice: {user_msg}
    {char_name} responde como si fuera real:
    """

    response = chat_with_togetherai(prompt)
    emit("response", response)


def chat_with_togetherai(prompt):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    json_data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "Respondé como el personaje, de forma natural."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
    }

    res = requests.post(url, headers=headers, json=json_data)
    if res.status_code == 200:
        return res.json()["choices"][0]["message"]["content"]
    else:
        return "Error al hablar con la IA."


# ✅ Corrected main block (ONLY ONCE)
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080, allow_unsafe_werkzeug=True)

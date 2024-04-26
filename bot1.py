import json
from telethon.sync import TelegramClient
from telethon.tl.types import InputMessagesFilterEmpty
from telethon.errors import SessionPasswordNeededError
import schedule
import time

def cargar_datos_desde_json(archivo_config, numero_bot):
    with open(archivo_config) as config_file:
        config_data = json.load(config_file)
        return (
            config_data[f'api_id'],
            config_data[f'api_hash'],
            config_data[f'grupos_a_evitar'],
            config_data[f'grupo_origen_id{numero_bot}'],
            config_data[f'tu_numero_telefono{numero_bot}']
        )

def iniciar_sesion(api_id, api_hash, tu_numero_telefono):
    client = TelegramClient('session_name1', api_id, api_hash)
    client.connect()
    if not client.is_user_authorized():
        try:
            client.send_code_request(tu_numero_telefono)
            client.sign_in(tu_numero_telefono, input('Ingresa el código que has recibido: '))
        except SessionPasswordNeededError:
            client.sign_in(password=input('Ingresa la contraseña de la cuenta: '))
    return client

def reenviar_mensajes(client, grupo_origen_id, grupos_a_evitar):
    try:
        messages = client.get_messages(grupo_origen_id, filter=InputMessagesFilterEmpty())
        
        for message in messages:
            chats = client.get_dialogs()
            for chat in chats:
                if chat.is_group and chat.id != grupo_origen_id and chat.id not in grupos_a_evitar:
                    client.forward_messages(chat.id, messages=message)
                    print(f"Mensajes reenviados al grupo {chat.title}")
    except Exception as e:
        print(f"Error al reenviar mensajes: {e}")

def enviar_mensajes_periodicamente(client, grupo_origen_id, grupos_a_evitar):
    schedule.every(3.0).minutes.do(reenviar_mensajes, client, grupo_origen_id, grupos_a_evitar)
    while True:
        tiempo_restante = schedule.idle_seconds()
        print(f"Próximo reenvío en {tiempo_restante} segundos")
        schedule.run_pending()
        time.sleep(2)

if __name__ == "__main__":
    numero_bot = 1  # Puedes cambiar esto según el bot que estás ejecutando (1, 2, 3, etc.)
    api_id, api_hash, grupos_a_evitar, grupo_origen_id, tu_numero_telefono = cargar_datos_desde_json('config.json', numero_bot)

    client = iniciar_sesion(api_id, api_hash, tu_numero_telefono)
    enviar_mensajes_periodicamente(client, grupo_origen_id, grupos_a_evitar)
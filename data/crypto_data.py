import requests
import pandas as pd
import requests
import streamlit as st

global balance_usuario,portafolio, historial_transacciones
balance_usuario = 10000
portafolio = {}
historial_transacciones = []

def obtener_precio_actual(cripto_id):
    cripto_id = cripto_id.lower()
    
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={cripto_id}"
    try:
        response = requests.get(url)
        data = response.json()


        if isinstance(data, list) and len(data) > 0:
            try:
                return data[0]['current_price']
            except (KeyError, IndexError) as e:
                st.error(f"No se pudo obtener el precio de la criptomoneda. Error: {e}")
                return None
        else:
            st.error("Error de request 429: La respuesta no contiene datos.")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error al hacer la solicitud a la API: {e}")
        return None

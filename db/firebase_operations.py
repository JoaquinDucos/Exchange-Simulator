# db/firebase_operations.py
import requests
import json

firebase_project_id = 'crypto-trade-simulator'
firebase_api_key = 'Mi API'

def estructurar_valor_para_firestore(value):
    if isinstance(value, int):
        return {"integerValue": str(value)}
    elif isinstance(value, float):
        return {"doubleValue": value}
    elif isinstance(value, str):
        return {"stringValue": value}
    else:
        raise TypeError(f"Tipo de dato no soportado: {type(value)}")

def estructurar_datos_para_firestore(datos_a_guardar):
    estructurados = {}
    
    # Añade balance_usuario como un número (doubleValue para compatibilidad con Firestore)
    estructurados['balance_usuario'] = {"doubleValue": datos_a_guardar['balance_usuario']}
    
    # Añade portafolio como un mapa
    estructurados['portafolio'] = {
        "mapValue": {
            "fields": {k: {"doubleValue": v} for k, v in datos_a_guardar['portafolio'].items()}
        }
    }
    
    # Añade historial_transacciones como un array
    estructurados['historial_transacciones'] = {
        "arrayValue": {
            "values": [
                {
                    "mapValue": {
                        "fields": {
                            'tipo': {"stringValue": trans['tipo']},
                            'cripto_id': {"stringValue": trans['cripto_id']},
                            'cantidad': {"doubleValue": trans['cantidad']},
                            'precio': {"doubleValue": trans['precio']},
                            'total': {"doubleValue": trans['total']}
                        }
                    }
                } for trans in datos_a_guardar['historial_transacciones']
            ]
        }
    }
    
    return {"fields": estructurados}

def guardar_datos_en_firestore(documento_id, datos_a_guardar):
    url = f"https://firestore.googleapis.com/v1/projects/{firebase_project_id}/databases/(default)/documents/transacciones/{documento_id}?key={firebase_api_key}"
    payload = estructurar_datos_para_firestore(datos_a_guardar)
    response = requests.patch(url, json=payload)
    if response.status_code == 200:
        print("Datos guardados con éxito.")
    else:
        print(f"Error al guardar datos: {response.status_code} {response.text}")


def recuperar_datos_de_firestore(documento_id):
    documento_id = documento_id.strip()  # Elimina espacios extra
    url = f"https://firestore.googleapis.com/v1/projects/{firebase_project_id}/databases/(default)/documents/transacciones/{documento_id}?key={firebase_api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print("\nTodavía no existen datos, vamos a crearlos...\n")    
    else:
        print(f"\nError al recuperar datos de Firestore: {response.status_code} {response.text}\n")
        return None


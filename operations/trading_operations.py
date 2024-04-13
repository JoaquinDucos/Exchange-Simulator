from data.crypto_data import obtener_precio_actual, balance_usuario, historial_transacciones, portafolio
import json 
TASA_COMISION = 0.001

def guardar_datos():
    global balance_usuario, portafolio, historial_transacciones
    datos = {
        'balance_usuario': balance_usuario,
        'portafolio': portafolio,
        'historial_transacciones': historial_transacciones
    }
    with open('datos_usuario.json', 'w') as archivo:
        json.dump(datos, archivo)


def extraer_datos(documento):
    # Extraaig directamente el balance de usuario
    balance_usuario = documento.get('fields', {}).get('balance_usuario', {}).get('doubleValue', 10000)
    portafolio_campos = documento.get('fields', {}).get('portafolio', {}).get('mapValue', {}).get('fields', {})    
    portafolio = {k: v.get('doubleValue', 0) for k, v in portafolio_campos.items()}

    # Extraigo el historial de transacciones, que es una lista de diccionarios anidados
    historial_lista = documento['fields']['historial_transacciones']['arrayValue']['values']
    historial_transacciones = []
    for item in historial_lista:
        trans_fields = item['mapValue']['fields']
        transaccion = {
            "tipo": trans_fields['tipo']['stringValue'],
            "cripto_id": trans_fields['cripto_id']['stringValue'],
            "cantidad": trans_fields['cantidad']['doubleValue'],
            "precio": trans_fields['precio']['doubleValue'],
            "total": trans_fields['total']['doubleValue']
        }
        historial_transacciones.append(transaccion)

    return balance_usuario, portafolio, historial_transacciones


def mapeo(historial_transacciones):
    valor_inicial_por_cripto = {}

    for transaccion in historial_transacciones:
        if transaccion['tipo'] == 'compra':
            cripto_id = transaccion['cripto_id']
            total_compra = transaccion['total']

            if cripto_id in valor_inicial_por_cripto:
                valor_inicial_por_cripto[cripto_id] += total_compra
            else:
                valor_inicial_por_cripto[cripto_id] = total_compra

    return valor_inicial_por_cripto
import streamlit as st
from time import sleep
from data.crypto_data import obtener_precio_actual
from operations.trading_operations import mapeo, extraer_datos
from db.firebase_operations import recuperar_datos_de_firestore, guardar_datos_en_firestore

BALANCE_INICIAL_USUARIO = 10000
TASA_COMISION = 0.001
ganancias_ventas = 0
documento_id = 'Número de documento de almacenamiento en firebase'  

estado_anterior = recuperar_datos_de_firestore(documento_id)
if estado_anterior:
    balance_usuario, portafolio, historial_transacciones = extraer_datos(estado_anterior)
else:
    balance_usuario = BALANCE_INICIAL_USUARIO
    portafolio = {}
    historial_transacciones = []

precio_actual = 0

st.title('Simulador de Trading de Criptomonedas')
cripto_id = portafolio.keys()

# Mostrar balance del usuario y portafolio actual
st.write(f"Balance: ${balance_usuario:.2f}")

# Inicialización de variables en el estado de la sesión
if 'cripto_id_compra' not in st.session_state:
    st.session_state.cripto_id_compra = 'Bitcoin, Ethereum, Polkadot, etc...'

if 'cantidad_compra' not in st.session_state:
    st.session_state.cantidad_compra = 0.0

if 'maximo_posible' not in st.session_state:
    st.session_state.maximo_posible = 0.0

if 'precio_actual' not in st.session_state:
    st.session_state['precio_actual'] = 0

precio_actual = 0
costo_total=0
st.subheader('Compra de Criptomonedas')
cripto_id_compra = st.text_input("ID de la criptomoneda (ej: bitcoin, ethereum)", key='cripto_id_compra')

# Botón para confirmar selección y calcular el máximo posible
confirmar_seleccion = st.button("Confirmar Selección")


if confirmar_seleccion:
    precio_actual = obtener_precio_actual(cripto_id_compra)

    if precio_actual:
        st.session_state['precio_actual'] = precio_actual

        st.session_state['maximo_posible'] = (balance_usuario / precio_actual) -((balance_usuario / precio_actual) * TASA_COMISION)
        st.write(f"Puedes comprar hasta {st.session_state['maximo_posible']:.6f} {cripto_id_compra}.")
        st.write("Precio Actual: $", precio_actual)
    else:
        st.error("ID de criptomoneda no válido o no se pudo obtener el precio actual.")

# Sección para elegir la cantidad y realizar la compra
if st.session_state['cripto_id_compra'] and st.session_state.get('precio_actual', 0) > 0:
    
    usar_maximo = st.checkbox("Utilizar máximo disponible")

    if usar_maximo:
        st.session_state['cantidad_compra'] = st.session_state.get('maximo_posible', 0)
        valor_moneda_compra = (st.session_state.get('maximo_posible', 0) * precio_actual)
        costo_total = valor_moneda_compra* (1 + TASA_COMISION)
    
    cantidad_compra = st.number_input("Cantidad a comprar", min_value=0.0, max_value=st.session_state.get('maximo_posible', 0), step=0.001, value=st.session_state.get('cantidad_compra', 0), format="%.8f")
    
    precio_actual = obtener_precio_actual(cripto_id_compra)
    if precio_actual: 
        costo_total = precio_actual*cantidad_compra * (1 + TASA_COMISION)
    else:
        st.write("Error al obtener datos de la API")

    st.write(f"Costo total de la compra: ${costo_total:.2f} (incluyendo comisión).")
    

    confirmar_compra = st.button("Confirmar Compra")
    if confirmar_compra and precio_actual:
        if costo_total <= balance_usuario:
            balance_usuario -= costo_total
            portafolio[st.session_state['cripto_id_compra']] = portafolio.get(st.session_state['cripto_id_compra'], 0) + cantidad_compra
            historial_transacciones.append({
                'tipo': 'compra',
                'cripto_id': st.session_state['cripto_id_compra'],
                'cantidad': cantidad_compra,
                'precio': precio_actual,
                'total': costo_total
            })
            guardar_datos_en_firestore(documento_id, {
                'balance_usuario': balance_usuario,
                'portafolio': portafolio,
                'historial_transacciones': historial_transacciones      
            })
            st.success(f"Compra exitosa de {cantidad_compra} {st.session_state['cripto_id_compra']} por ${costo_total:.2f} (incluyendo comisión).")
            st.write(f"Balance actualizado: ${balance_usuario:.2f}")
        else:
            st.error("Fondos insuficientes para completar esta compra.")
        # Limpiar el estado para nuevas operaciones
        del costo_total


st.subheader("Vende tus criptoactivos")
# Crear un único selectbox para la selección de criptomonedas

if 'cripto_seleccionada' not in st.session_state:
    st.session_state['cripto_seleccionada']=''

opciones_cripto = list(portafolio.keys())

with st.expander("Elige la criptomoneda a vender:"):
    for cripto in opciones_cripto[0:]:  # Ignorar '' que es el primer elemento
        if st.button(cripto, key=cripto):
            st.session_state['cripto_seleccionada'] = cripto


# Utiliza el valor de 'cripto_seleccionada' para realizar operaciones subsiguientes
if st.session_state['cripto_seleccionada'] != '':
    # Realiza operaciones basadas en la criptomoneda seleccionada
    cantidad_disponible_venta = float(portafolio.get(st.session_state['cripto_seleccionada'], 0))
    precio_actual_venta = obtener_precio_actual(st.session_state['cripto_seleccionada'])
    
    if precio_actual_venta:
        st.write(f"Tienes {cantidad_disponible_venta:.6f} monedas de {st.session_state['cripto_seleccionada']}.")
        st.write(f"Precio actual de {st.session_state['cripto_seleccionada']}: ${precio_actual_venta:.2f} USD")
        with st.form(key='form_vender'):
            cantidad_venta = st.number_input("Cantidad a vender", min_value=0.0, max_value=cantidad_disponible_venta, value=0.0, step=0.001, format="%.3f")
            
            # Botón para calcular el valor estimado de la venta antes de comisión
            boton_calcular_valor = st.form_submit_button("Calcular Valor de Venta")

        if boton_calcular_valor:
            # Calcular el valor de la venta antes de la comisión
            valor_venta_sin_comision = cantidad_venta * precio_actual_venta
            comision = valor_venta_sin_comision * TASA_COMISION
            valor_venta_final = valor_venta_sin_comision - comision
            valor_inicial_por_cripto = []

            valor_inicial_por_cripto = mapeo(historial_transacciones)
            ganancia_venta_individual = valor_venta_final - (valor_inicial_por_cripto.get(cripto_id, 0) * cantidad_venta)
            ganancias_ventas += ganancia_venta_individual

            st.write(f"Valor estimado de la venta (antes de comisión): ${valor_venta_sin_comision:.2f} USD")
            st.write(f"Comisión estimada: ${comision:.2f} USD")
            st.write(f"Valor final estimado de la venta (después de comisión): ${valor_venta_final:.2f} USD")

            # Opción para confirmar la venta después de revisar el valor estimado
            if st.button("Confirmar Venta"):
                balance_usuario += valor_venta_final
                portafolio[st.session_state['cripto_seleccionada']] -= cantidad_venta
                if portafolio[st.session_state['cripto_seleccionada']] == 0:
                    del portafolio[st.session_state['cripto_seleccionada']]
                    
                historial_transacciones.append({
                    'tipo': 'venta',
                    'cripto_id': st.session_state['cripto_seleccionada'],
                    'cantidad': cantidad_venta,
                    'precio': precio_actual_venta,
                    'total': valor_venta_final
                })
                st.success(f"Venta exitosa de {cantidad_venta} {st.session_state['cripto_seleccionada']} por ${valor_venta_final:.2f} USD (después de comisión).")
                st.write(f"Balance actualizado: ${balance_usuario:.2f} USD")
    else:
        st.error(f"No se pudo obtener el precio actual de {st.session_state['cripto_seleccionada']}. Por favor, intenta nuevamente.")
else:
    st.write("Por favor, selecciona una criptomoneda para vender.")


valor_inicial_por_cripto = mapeo(historial_transacciones)

st.subheader("Tu Portafolio")

with st.expander('Cripto Activos'):
    valor_total_portafolio = 0
    valor_inicial_total = 0
    ganancia_perdida = 0
    errores_encontrados = False

    st.subheader("Monedas/Tokens")
    for cripto_id, cantidad in portafolio.items():
        try:
            precio_actual_portafolio = obtener_precio_actual(cripto_id)
            if precio_actual_portafolio is not None:
                valor_cripto = precio_actual_portafolio * cantidad
                valor_total_portafolio += valor_cripto

                valor_inicial = valor_inicial_por_cripto.get(cripto_id, 0)
                valor_inicial_total += valor_inicial

                st.write(f"{cripto_id}: {cantidad} unidades - Valor actual: ${valor_cripto:.2f}")
            else:
                raise ValueError("Precio actual no disponible.")
        except Exception as e:
            st.error(f"Error al obtener precio para {cripto_id}: {str(e)}")
            errores_encontrados = True
            break

    if not errores_encontrados:
        ganancia_perdida = valor_total_portafolio - valor_inicial_total
        porcentaje_balance = ((balance_usuario + ganancia_perdida) / BALANCE_INICIAL_USUARIO - 1) * 100
        balance_total = balance_usuario + valor_total_portafolio
        porcentaje_balance_total = ((balance_total / BALANCE_INICIAL_USUARIO - 1) * 100)

        st.subheader("Balances: ")
        st.write(f"Valor Actual del Portafolio: ${valor_total_portafolio:.2f}")
        st.write(f"Costo Real del Portafolio: ${valor_inicial_total:.2f}")
        st.write(f"Balance en Efectivo: ${balance_usuario:.2f}  ({porcentaje_balance:.4f}%)")
        st.write(f"Ganancias/Pérdidas actuales del portafolio: ${ganancia_perdida:.2f}")
        st.write(f"Balance Total de la cuenta: ${balance_total:.2f}  ({porcentaje_balance_total:.4f}%)")

    


from data.crypto_data import *
from operations.trading_operations import *
from db.firebase_operations import recuperar_datos_de_firestore, guardar_datos_en_firestore
BALANCE_INICIAL_USUARIO = 10000
TASA_COMISION = 0.001

documento_id = 'Número de documento de firebase'  

print("Estamos recuperando información de nuestra base de datos, aguarde unos segundos...")

estado_anterior = recuperar_datos_de_firestore(documento_id)
if estado_anterior:
    balance_usuario, portafolio, historial_transacciones = extraer_datos(estado_anterior)
    print("\nSe ha recuperado la información de su cuenta\n")
    
else:
    # Estado inicial del Usuario si es la primera vez
    print("\n***********************************************************************************************************************")
    print("\n***********************************************************************************************************************")
    print("\n\nBienvenido al SIMULADOR DE CRIPTO-TRADING! Actualmente tienes $10.000 USD para que empieces con el trading. Éxitos!\n\n")
    print("\n***********************************************************************************************************************")
    print("\n***********************************************************************************************************************")
    balance_usuario:10000
    portafolio = {}
    historial_transacciones=[]

while True:
    ganancias_ventas = 0

    accion = input("\n¿Quieres comprar (c), vender (v), imprimir portfolio(p), mostrar historial de trans.(h) o salir (s)? ")
    if accion == 's':

        guardar_datos_en_firestore(documento_id, {
            'balance_usuario': balance_usuario,
            'portafolio': portafolio,
            'historial_transacciones': historial_transacciones      
            })
        valor_total_portafolio = 0
        break


    elif accion in ['c', 'v']:
        maximo_posible = 0
        cripto_id = input("\nIngresa el ID de la criptomoneda (ej: bitcoin, ethereum): ")
        precio_actual = obtener_precio_actual(cripto_id)
        print("\nRecuerda que la comisión por cada operación es del 0.1%\n")
        confirmar_compra = 's'
        if precio_actual == "Inexistente":
               print("\n\nPuede que el criptoactivo que estes buscando no exista o esté mal escrito! Prueba nuevamente.\n\n")

        elif accion == 'c':
            maximo_posible = balance_usuario / (precio_actual * (1 + TASA_COMISION))
            print("\nPrecio actual de ",cripto_id, " = $USD", precio_actual)
            print(f"\nTienes ${balance_usuario:.2f} USD. Puedes comprar hasta {maximo_posible:.6f} {cripto_id}, considerando la comisión.")

            usar_maximo = input("¿Quieres usar el máximo disponible para comprar? (s/n): ").lower()
            if usar_maximo == 's':
                cantidad = maximo_posible
            else:
                cantidad = float(input("Ingresa la cantidad que deseas comprar: "))
            
            costo = cantidad * precio_actual
            comision = costo * TASA_COMISION
            costo += comision
            print(f"\nDesea comprar {cantidad} {cripto_id} por: $USD{costo} total?")
            confirmar_compra = input("\nIngrese 's' para aceptar compra, o cualquier otro botón para rechazar: ")

            
            if balance_usuario >= costo and confirmar_compra == 's':
                balance_usuario -= costo
                print("\nCompra exitosa!\n")

                # Asegurarse de que estamos modificando el portafolio global
                if cripto_id in portafolio:
                    portafolio[cripto_id] += cantidad
            
                print("Valor total en USD: $",costo)
                historial_transacciones.append({'tipo': 'compra','cripto_id': cripto_id, 'cantidad': cantidad, 'precio': precio_actual, 'total': costo})
                elemento_nuevo = {cripto_id: cantidad}
                for clave, valor in elemento_nuevo.items():
                    if clave in portafolio:
                        # Verifica si ambos, el valor en historial_transacciones y el valor en elemento_nuevo, son números
                        if isinstance(portafolio[clave], (int, float)) and isinstance(valor, (int, float)):
                            # Resta el valor si la clave existe y ambos valores son numéricos
                            portafolio[clave] += valor
                        else:
                    # Si no son numéricos, podrías elegir reemplazar, ignorar, o manejar de otra manera
                            print(f"No se puede restar, ya que al menos uno de los valores para '{clave}' no es numérico.")
                    else:
                        portafolio.update(elemento_nuevo)

            else:
                if confirmar_compra != 's':
                    print("\nOrden cancelada con éxito!")
                else:
                    print("\nFondos insuficientes para realizar la compra.")

        else:
            cantidad_disponible = portafolio.get(cripto_id, 0)
            print(f"Tienes {cantidad_disponible:.6f} monedas de {cripto_id}.")

            print("\nPrecio actual de ",cripto_id, " = $USD", precio_actual)
            usar_maximo = input("\n¿Quieres vender el máximo disponible? (s/n): ").lower()
            if usar_maximo == 's':
                cantidad = cantidad_disponible
            else:
                cantidad = float(input("\nIngresa la cantidad que deseas vender: "))

            print("\nRecuerda que la comisión por cada operación es del 0.1%\n")

            costo = cantidad * precio_actual
            comision = costo * TASA_COMISION
            costo -= comision

            print(f"\nDesea vender {cantidad} {cripto_id} por: $USD{costo}  (Valor final con comisón incluida)")
            confirmar_compra = input("\nIngrese 's' para realizar la venta, o cualquier otro botón para rechazar: ")
            # Verifica si la criptomoneda ya existe en el portafolio y si la cantidad a vender no supera la cantidad disponible
           
            if cripto_id in portafolio and cantidad <= portafolio[cripto_id] and confirmar_compra == 's':
                # Procede con la venta
                print("\nVenta exitosa!\n")
                venta_realizada = precio_actual * cantidad
                balance_usuario += venta_realizada  # Actualiza el balance del usuario
                portafolio[cripto_id] -= cantidad  # Actualiza la cantidad de criptomoneda en el portafolio
                valor_inicial_por_cripto = mapeo(historial_transacciones)
                ganancia_venta_individual = venta_realizada - (valor_inicial_por_cripto.get(cripto_id, 0) * cantidad)
                ganancias_ventas += ganancia_venta_individual
                # Elimina la criptomoneda del portafolio si la cantidad llega a cero
                if portafolio[cripto_id] == 0:
                    del portafolio[cripto_id]    
                print(f"Valor total en USD: ${venta_realizada:.3f}")
                
                print(f"balance del usuario actualizado: {balance_usuario:.3f}")
                historial_transacciones.append({'tipo': 'venta','cripto_id': cripto_id, 'cantidad': cantidad, 'precio': precio_actual, 'total': precio_actual * cantidad})
            else:
                # Si no existe la criptomoneda en el portafolio o no hay suficiente cantidad para vender, muestra un mensaje de error
                if cripto_id not in portafolio:
                    print("\nNOTA: \n       No puedes vender esta criptomoneda porque no tienes ninguna en tu portafolio.\n")
                elif confirmar_compra !='s':    
                    print("\nOrden cancelada con éxito!")
                else:
                    print("\nNOTA: \n       No puedes vender esta cantidad de criptomoneda porque excede tu reserva disponible.")
            

    elif accion == 'p':  # Para imprimir el resumen del portafolio
        print("\n     TUS MONEDAS:     \n")
        valor_total_portafolio = 0
        valor_inicial_total = 0
        balance_total = 0

        valor_inicial_por_cripto = mapeo(historial_transacciones)

        for cripto_id, cantidad in portafolio.items():

            precio_actual = obtener_precio_actual(cripto_id)
            valor_cripto = precio_actual * cantidad
            valor_total_portafolio += valor_cripto

            valor_inicial = valor_inicial_por_cripto.get(cripto_id, 0)
            valor_inicial_total += valor_inicial    
            print(f"\n{cripto_id}: {cantidad} Monedas\nValor compra inicial: {valor_inicial:.3f}\nValor actual: ${valor_cripto:.3f}")
    

        ganancia_perdida = (valor_total_portafolio + ganancias_ventas - valor_inicial_total)  
        porcentaje_balance = ((balance_usuario *100 + ganancia_perdida)/BALANCE_INICIAL_USUARIO) - 100
        
        balance_total = balance_usuario + valor_total_portafolio
        porcentaje_balance_total = ((balance_total *100 )/BALANCE_INICIAL_USUARIO) - 100
        print(f"\nValor Actual del Portafolio: ${valor_total_portafolio:.2f}")
        print(f"\nCosto Real del Portafolio: ${valor_inicial_total:.2f}")
        print(f"\nBalance en Efectivo: ${balance_usuario:.2f}  ({porcentaje_balance:.4f}%)")
        print(f"\nGanancias/Pérdidas actuales del portafolio: ${ganancia_perdida:.2f}\n")
        print(f"\nBalance Total de la cuenta: ${balance_total:.2f}  ({porcentaje_balance_total:.4f}%)")


    elif accion == 'h':  # Para ver el historial de transacciones
        for transaccion in historial_transacciones:
            print(transaccion)  


    else:
        print("\nAcción no reconocida.")


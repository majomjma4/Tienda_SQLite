
import sqlite3
from datetime import datetime

DB_FILE = "tienda.db"

def conectar():
    return sqlite3.connect(DB_FILE)

def inicializar_bd():
    with conectar() as conn:
        c = conn.cursor()
        
        c.execute("""
                  CREATE TABLE IF NOT EXISTS catalogo (
                    codigo   TEXT     PRIMARY KEY,
                    nombre   TEXT     NOT NULL,
                    precio   REAL     NOT NULL,
                    stock    INTEGER  NOT NULL
                )""")
        
        c.execute("""
                  CREATE TABLE IF NOT EXISTS  carrito (
                    codigo     TEXT,
                    nombre     TEXT,
                    precio     REAL,
                    cantidad   INTEGER,
                    FOREING KEY (codigo) REFERENCES catalogo(codigo)
                      
                )""")
        
        c.execute("""
                  CREATE TABLE IF NOT EXISTS ventas (
                    id      INTEGER    PRIMARY KEY    AUTOINCREMENT,
                    ticket  TEXT       NOT NULL,
                    fecha   TEXT       NOT NULL 
                )""")
        
        conn.commit()

def leer_archivo(nombre_archivo):
    if not os.path.exists(nombre_archivo):
        open(nombre_archivo, 'w', encoding='utf-8').close()
    with open(nombre_archivo, 'r', encoding = 'utf-8') as f: return f.readlines()
    
def escribir_archivo(nombre_archivo, lineas, modo ='w'):
    with open(nombre_archivo, modo, encoding='utf-8') as f: f.writelines(lineas)

def cargar_catalogo():
    catalogo.clear()
    for linea in leer_archivo(CATALOGO_FILE):
        partes = linea.strip().split(",")
        if len(partes) == 4:
            try:
                codigo, nombre, precio, stock = partes 
                catalogo.append({
                    'codigo': codigo.strip().upper(),
                    'nombre': nombre.strip(),
                    'precio': float(precio.strip()),
                    'stock': int(stock.strip())
                })
            except ValueError:
                continue

def guardar_catalogo():
    lineas = [f"{product['codigo']},{product['nombre']},{product['precio']},{product['stock']}\n" for product in catalogo]
    escribir_archivo(CATALOGO_FILE, lineas)
            
def ver_catalogo():
        if not catalogo: print("Catálogo vació. "); return
        
        print("\n------ CATÁLOGO ------")
        for product in catalogo:
            print(f"{product['codigo']} | {product['nombre']} | ${product['precio']:.2f} | {product['stock']} ")
      
def agregar_producto():
    codigo = input("Ingrese el código del producto: ").strip().upper()
    if not codigo or any(product['codigo'] == codigo for product in catalogo): print("Código inválido o existente "); return
         
    nombre = input("Ingrese el nombre del producto: ").strip()
    if not nombre: print("El nombre no puede estar vacío."); return
    
    try:
        precio = float(input("Ingrese el precio del producto: ").strip())
        stock = int(input("Ingrese la cantidad de producto en stock: ").strip())
        if precio <= 0 or stock < 0: raise ValueError
        
    except ValueError: print("Datos inválidos. Precio debe ser > 0 y stock >= 0 "); return
    catalogo.append({'codigo': codigo,'nombre': nombre, 'precio': precio, 'stock': stock })
    guardar_catalogo(); print(f"Producto {nombre} agregado al catálogo. ")

def cargar_carrito():
    carrito.clear()
    for linea in leer_archivo(CARRITO_FILE):
        partes = linea.strip().split(',')
        if len(partes)== 4:
            try:
                codigo,nombre,precio,cantidad = partes
                carrito.append({
                    'codigo': codigo.strip(),
                    'nombre': nombre.strip(),
                    'precio': float(precio.strip()),
                    'cantidad': int(cantidad.strip())
                })
            except ValueError: 
                continue
            
def guardar_carrito():
    lineas = [f"{car['codigo']},{car['nombre']},{car['precio']},{car['cantidad']}\n" for car in carrito]
    escribir_archivo(CARRITO_FILE, lineas)        

def agregar_carrito():
    cargar_carrito()
    codigo = input("Ingrese el código del producto que desea agregar al carrito: ").strip().upper()
    producto = next((product for product in catalogo if product['codigo'] == codigo), None)
    if not producto: print("Producto no encontrado"); return
    try: cantidad = int(input("Ingrese la cantidad a comprar: ").strip()); assert cantidad>0    
    except: print("Cantidad inválida. Debe ser un número entero mayor a 0."); return
        
    if cantidad > producto['stock']: print(f"Stock insuficiente. Disponible: {producto['stock']}"); return
    
    item = next((car for car in carrito if car['codigo'] == codigo), None)
    if item: item['cantidad'] += cantidad
    else: carrito.append({'codigo': producto['codigo'], 'nombre': producto['nombre'], 'precio': producto['precio'], 'cantidad': cantidad})
    producto['stock'] -= cantidad
    
    guardar_catalogo(); guardar_carrito()
    print(f"{cantidad} unidades de {producto['nombre']} ha sido agregado al carrito")
       
def ver_carrito():
    cargar_carrito()             
    if not carrito: print("Carrito vacío"); return
        
    total = 0
    print("\n--- CARRITO DE COMPRAS --- ")
    for car in carrito:
        subtotal = car['precio'] * car['cantidad']
        total += subtotal
        print(f"{car['nombre']} x {car['cantidad']} = ${subtotal:.2f}")
    print(f"Total: ${total:.2f}")
        
def finalizar_compra():
    cargar_carrito()
    if not carrito: print("Carrito vacío"); return
    if input("Desea finalizar la compra (si/no): ").strip().lower()!= 'si': print("Compra cancelada"); return
   
    total = sum(car['precio'] * car['cantidad'] for car in carrito)
    iva = total * 0.15; 
    subtotal_iva = total + iva
    descuento = 0.10 if subtotal_iva > 50 else 0.05 if subtotal_iva > 20 else 0
    total_final = subtotal_iva * (1-descuento)
    
    ticket = f"\n{'='*40}\nFACTURA \nFecha: {datetime.now()}\n {"-" * 40}\n"
    for car in carrito:
        subtotal_producto = car['precio'] * car['cantidad']
        subtotal_producto_iva = subtotal_producto * 1.15
        ticket += f"{car['nombre']} x {car['cantidad']} = ${subtotal_producto:.2f}\n "
        
    ticket += f"\nTotal sin IVA: ${total:.2f}\n"
    ticket += f"IVA 15%: ${iva:.2f}\n Subtotal con IVA: ${subtotal_iva:.2f}\n "
    
    if descuento > 0: ticket += f"Descuento: {int(descuento*100)}%\n"
    ticket += f"TOTAL A PAGAR: ${total_final:.2f}\n{'='*40}\n"
    print(ticket)
    
    registrar_venta(ticket)
    carrito.clear()
    guardar_carrito()
    guardar_catalogo()
        
def registrar_venta(ticket):escribir_archivo(VENTAS_FILE, [ticket], modo='a')        
    
def ver_ventas():
    if not os.path.exists(VENTAS_FILE): print("No hay ventas registradas"); return
    ventas_todas = "".join(leer_archivo(VENTAS_FILE))
    opcion = input("Desea ver todas las ventas o buscar una venta especifica? (todas/buscar): ").strip().lower()
    if opcion == "todas": print(ventas_todas)
    elif opcion == "buscar":
        search = input("Ingrese la palabra clave para buscar (producto o fecha): ").strip().lower()
        ventas_filtradas =[ventas for ventas in ventas_todas.split('='*40)if search in ventas.lower()]
        print("\n".join(ventas_filtradas) if ventas_filtradas else "No se encontraron ventas con esa palabra clave. " )
    else:
        print("Opción inválida")
    
if __name__=="__main__":
    cargar_catalogo(); cargar_carrito()
    while True:
        print("""
    \nEscoja una opción:
    1. Ver catálogo
    2. Agregar al carrito
    3. Ver carrito
    4. Finalizar compra
    5. Ver ventas
    6. Agregar Producto 
    0. Salir
    \n""")
        opcion = input("\nIngrese la opción: ").strip()
        if opcion == "1": ver_catalogo()
        elif opcion == "2": agregar_carrito()
        elif opcion == "3": ver_carrito()
        elif opcion == "4": finalizar_compra()
        elif opcion == "5": ver_ventas()
        elif opcion == "6": agregar_producto()
        elif opcion == "0": print("¡Gracias por preferirnos! Hasta luego"); break
        else: print("Opción inválida")
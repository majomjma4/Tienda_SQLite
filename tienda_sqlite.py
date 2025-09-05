
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
                    FOREIGN KEY (codigo) REFERENCES catalogo(codigo)
                      
                )""")
        
        c.execute("""
                  CREATE TABLE IF NOT EXISTS ventas (
                    id      INTEGER    PRIMARY KEY    AUTOINCREMENT,
                    ticket  TEXT       NOT NULL,
                    fecha   TEXT       NOT NULL 
                )""")
        
        conn.commit()
  
def ver_catalogo():
    with conectar() as conn:
        c = conn.cursor()
        c.execute("SELECT codigo, nombre, precio, stock FROM catalogo ORDER BY nombre")
        productos = c.fetchall()
        if not productos: print("Catálogo vacío."); return
        print("\n------ CATÁLOGO ------")
        for codigo, nombre, precio, stock in productos:
            print(f"{codigo} | {nombre} | ${precio:.2f} | {stock} ")
      
def agregar_producto():
    producto = input("Ingrese el producto en el formato (codigo, nombre, precio, stock): ").strip()
    try:
        codigo, nombre, precio, stock = [x.strip() for x in producto.split(',')]
        codigo = codigo.upper()
        precio = float(precio)
        stock = int(stock)
        
        if not codigo or not nombre or precio <= 0 or stock <0:
            raise ValueError
    except Exception:
        print("Formato incorrecto. Use: codigo, nombre, precio, stock")
        return
    
    with conectar() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM catalogo WHERE codigo =?", (codigo,))
        if c.fetchone(): print("Código existente. "); return
         
        c.execute("INSERT INTO catalogo VALUES (?,?,?,?)", (codigo, nombre, precio, stock))
        conn.commit()
        print(f"Producto {nombre} agregado al catálogo.")
       
def agregar_carrito():
    codigo = input("Ingrese el código del producto que desea agregar al carrito: ").strip().upper()
    with conectar() as conn:
        c = conn.cursor()
        c.execute("SELECT nombre, precio, stock FROM catalogo WHERE codigo =?", (codigo,))
        producto = c.fetchone()
    
        if not producto: 
            print("Producto no encontrado")
            return
        nombre, precio, stock = producto
            
        try: cantidad = int(input("Ingrese la cantidad a comprar: ").strip()); assert cantidad>0    
        except: print("Cantidad inválida. Debe ser un número entero mayor a 0."); return
            
        if cantidad > stock: print(f"Stock insuficiente. Disponible: {stock}"); return
        
        c.execute("SELECT cantidad FROM carrito WHERE codigo =?", (codigo,))
        item = c.fetchone()
    
        if item: 
            c.execute("UPDATE carrito SET cantidad = cantidad +? WHERE codigo=?", (cantidad, codigo))
        else:
            c.execute("INSERT INTO carrito VALUES (?,?,?,?)", (codigo, nombre, precio, cantidad))
        
        c.execute("UPDATE catalogo SET stock = stock -? WHERE codigo =?", (cantidad, codigo))
        conn.commit()
        print(f"{cantidad} unidades de {nombre} ha sido agregado al carrito")
       
def ver_carrito():
    with conectar() as conn: 
        c= conn.cursor()
        c.execute("SELECT nombre, precio, cantidad FROM carrito ORDER BY nombre")
        carrito = c.fetchall()           
        if not carrito: print("Carrito vacío"); return
        
        total = 0
        print("\n--- CARRITO DE COMPRAS --- ")
        for nombre, precio, cantidad in carrito:
            subtotal = precio * cantidad
            total += subtotal
            print(f"{nombre} x {cantidad} = ${subtotal:.2f}")
        print(f"Total: ${total:.2f}")
        
def finalizar_compra():
    with conectar() as conn:
        c = conn.cursor()
        c.execute("SELECT codigo, nombre, precio, cantidad FROM carrito")
        carrito = c.fetchall()
        if not carrito: print("Carrito vacío"); return
        if input("Desea finalizar la compra (si/no): ").strip().lower()!= 'si': print("Compra cancelada"); return
   
        total_sin_iva = sum(precio * cantidad for _, _, precio, cantidad in carrito)
        iva = total_sin_iva * 0.15; 
        subtotal_iva = total_sin_iva + iva
        descuento = 0.10 if subtotal_iva > 50 else 0.05 if subtotal_iva > 20 else 0
        total_final = subtotal_iva * (1-descuento)
        
        ticket = f"\n{'='*40}\nFACTURA \nFecha: {datetime.now()}\n {'-' * 40}\n"
        for _, nombre, precio, cantidad in carrito:
            subtotal_producto = precio * cantidad
            
            ticket += f"{nombre} x {cantidad} = ${subtotal_producto:.2f}\n "
            
        ticket += f"\nTotal sin IVA: ${total_sin_iva:.2f}\n"
        ticket += f"IVA 15%: ${iva:.2f}\n Subtotal con IVA: ${subtotal_iva:.2f}\n "
        
        if descuento > 0: ticket += f"Descuento: {int(descuento*100)}%\n"
        ticket += f"TOTAL A PAGAR: ${total_final:.2f}\n{'='*40}\n"
        print(ticket)
        
        c.execute("INSERT INTO ventas (ticket, fecha) VALUES (?,?)", (ticket, str(datetime.now())))
        c.execute("DELETE FROM carrito")
        conn.commit()
         
def ver_ventas():
    with conectar() as conn:
        c = conn.cursor()
        c.execute("SELECT ticket FROM ventas ORDER BY fecha DESC")
        ventas = c.fetchall()
        if not ventas: print("No hay ventas registradas"); return
        opcion = input("Desea ver todas las ventas o buscar una venta especifica? (todas/buscar): ").strip().lower()
        if opcion == "todas": 
            for v in ventas: print(v[0])
        elif opcion == "buscar":
            search = input("Ingrese la palabra clave para buscar (producto o fecha): ").strip().lower()
            resultados = [v[0] for v in ventas if search in v[0].lower()]
                    
            if resultados:
                for r in resultados: print(r)  
            else:
                print(f"No se encontraron ventas que coincidad con '{search}'")
        else:
            print("Opción inválida. Por favor ingrese 'todas' o 'buscar'")
    
if __name__=="__main__":
    inicializar_bd()
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
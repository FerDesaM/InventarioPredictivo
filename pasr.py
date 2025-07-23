import pandas as pd
from sqlalchemy import create_engine, text

# Parámetros de conexión desde DataGrip
usuario = 'postgres'
password = '123456'  # 👈 reemplaza esto por tu contraseña real
host = 'localhost'
puerto = '5432'
nombre_bd = 'farm'

# Crear motor de conexión
engine = create_engine(f'postgresql+psycopg2://{usuario}:{password}@{host}:{puerto}/{nombre_bd}')


def truncate_all():
    with engine.begin() as conn:
        for table in [
            "farmacia_app_venta",
            "farmacia_app_inventariofarmacia",
            "farmacia_app_manager",
            "farmacia_app_empleado",
            "farmacia_app_producto",
            "farmacia_app_farmacia",
        ]:
            conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
    print("✔ Todas las tablas truncadas")

def cargar_csv(path, tabla, rename_map, notnull_cols, date_cols=None):
    print(f"Cargando {path} → {tabla}")
    df = pd.read_csv(path)
    df = df.rename(columns=rename_map)
    if date_cols:
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        df = df.dropna(subset=date_cols)
    df = df.dropna(subset=notnull_cols)
    # Mantener solo columnas de modelo
    df = df.loc[:, rename_map.values()]
    df.to_sql(tabla, engine, if_exists='append', index=False)
    print(f"✔ {tabla} importada ({len(df)} filas)")

if __name__ == "__main__":
    truncate_all()

    cargar_csv(
      "farmacias.csv", "farmacia_app_farmacia",
      {"Pharmacy_ID":"id","Nombre_Farmacia":"nombre_farmacia",
       "Distrito":"distrito","Ciudad":"ciudad","País":"pais"},
      ["nombre_farmacia","distrito","ciudad","pais"]
    )

    cargar_csv(
      "productos.csv","farmacia_app_producto",
      {"Product_ID":"product_id","Nombre_Producto":"nombre_producto",
       "Clase":"clase","Precio_Unitario":"precio_unitario",
       "Fecha_Vencimiento":"fecha_vencimiento"},
      ["product_id","nombre_producto","clase","precio_unitario","fecha_vencimiento"],
      date_cols=["fecha_vencimiento"]
    )

    cargar_csv(
      "empleados.csv","farmacia_app_empleado",
      {"Empleado_id":"id","Nombre":"nombre","Apellido":"apellido",
       "DNI":"dni","Farmacia_ID":"farmacia_id","Pasword":"password","Es_admin":"es_admin"},
      ["nombre","apellido","dni","farmacia_id","password","es_admin"]
    )

    cargar_csv(
        "manager.csv",
        "farmacia_app_manager",
        rename_map={
            "Manager_ID": "id",
            "Nombre": "nombre",
            "Apellido": "apellido",
            "Farmacia_ID": "farmacia_id",
            "Password": "password",
            "Email": "email", 

        },
        notnull_cols=["nombre", "apellido", "farmacia_id", "password","email"]
    )

    cargar_csv(
      "inventario_farmacia.csv","farmacia_app_inventariofarmacia",
      {"Pharmacy_ID":"farmacia_id","Product_ID":"producto_id","Stock":"stock"},
      ["farmacia_id","producto_id","stock"]
    )

    cargar_csv(
      "ventas.csv","farmacia_app_venta",
      {"Codigo_venta":"codigo_venta","Product_id":"producto_id",
       "Empleado_id":"empleado_id","Quantity":"quantity",
       "Dia":"dia","Month":"month","Year":"year",
       "Sales":"sales","Igv":"igv","Total":"total",
       "Moneda":"moneda","Estado":"estado","Tipo_comp":"tipo_comp"},
      ["codigo_venta","producto_id","empleado_id","quantity",
       "dia","month","year","sales","igv","total","moneda","estado","tipo_comp"]
    )

    print("🏁 ¡Carga completa!")
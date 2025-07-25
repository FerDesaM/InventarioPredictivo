# Sistema de Inventario Predictivo para Farmacias

## Descripción General

Este proyecto es un sistema de gestión de inventario diseñado específicamente para farmacias, con un enfoque en la predicción de la demanda para optimizar el stock de productos. Desarrollado con Django, el sistema permite a los managers y empleados gestionar productos, registrar compras y ventas, y obtener predicciones sobre el agotamiento de inventario para una toma de decisiones más eficiente.

## Características Principales

-   **Gestión de Usuarios y Roles**: Diferenciación entre Managers y Empleados con distintos niveles de acceso.
-   **Gestión de Productos**: Registro y administración de productos farmacéuticos con detalles como nombre, clase, precio y fecha de vencimiento.
-   **Registro de Compras**: Funcionalidad para registrar las adquisiciones de productos a proveedores.
-   **Registro de Ventas**: Control de las ventas realizadas, asociadas a empleados y productos.
-   **Gestión de Inventario**: Mantenimiento del stock actual de productos en cada farmacia.
-   **Predicción de Demanda**: Algoritmos para prever el agotamiento de productos basados en el historial de ventas.
-   **Ranking de Empleados**: Visualización del rendimiento de ventas por empleado.
-   **Dashboard Interactivo**: Paneles de control para managers y empleados con información relevante y alertas.

## Tecnologías Utilizadas

-   **Backend**: Python 3.x, Django
-   **Base de Datos**: SQLite (por defecto, configurable para PostgreSQL, MySQL, etc.)
-   **Frontend**: HTML, CSS, JavaScript (con Django Templates)
-   **Librerías Python**: `django.contrib.auth`, `django.db.models`, `dateutil`, `collections`, etc.

## Estructura del Proyecto

El proyecto se organiza en las siguientes carpetas y archivos clave:

-   `InventarioPredictivo/` (Directorio raíz del proyecto)
    -   `farmaciaPredictiva_project/`: Configuración principal del proyecto Django.
        -   `settings.py`: Configuración de la base de datos, aplicaciones instaladas, etc.
        -   `urls.py`: Definición de las URLs globales del proyecto.
    -   `farmacia_app/`: Aplicación principal de Django para la lógica de negocio.
        -   `models.py`: Definición de los modelos de la base de datos (Farmacia, Producto, Empleado, Manager, InventarioFarmacia, Venta, Compra).
        -   `views.py`: Lógica de las vistas que manejan las solicitudes HTTP y renderizan las plantillas.
        -   `urls.py`: Definición de las URLs específicas de la aplicación `farmacia_app`.
        -   `admin.py`: Configuración para el panel de administración de Django.
        -   `tests.py`: Contiene las pruebas unitarias para modelos y vistas.
        -   `functional_tests.py`: Contiene las pruebas funcionales que simulan interacciones de usuario.
        -   `integration_tests.py`: Contiene las pruebas de integración que verifican la interacción entre componentes.
        -   `templates/`: Archivos HTML para la interfaz de usuario.
        -   `static/`: Archivos estáticos (CSS, JavaScript, imágenes).
    -   `manage.py`: Utilidad de línea de comandos de Django para tareas administrativas.
    -   `requirements.txt`: Lista de dependencias de Python del proyecto.
    -   `README.md`: Este archivo.
    -   `class_diagram.png`: Diagrama de clases del sistema.
    -   `documentacion_uso_pruebas.md`: Documentación sobre cómo ejecutar las pruebas.
    -   `documentacion_posibles_errores.md`: Documentación sobre errores comunes y soluciones.
    -   `informe_errores_corregidos.md`: Informe de errores que han sido corregidos.

## Diagrama de Clases

A continuación, se presenta el diagrama de clases que ilustra la estructura de los modelos de datos y sus relaciones en el sistema:

![Diagrama de Clases](https://private-us-east-1.manuscdn.com/sessionFile/ghwrfj97U6FCScaR2M3ZMs/sandbox/HLYcYMUEjMCBv2QF0tVIT7-images_1753459182715_na1fn_L2hvbWUvdWJ1bnR1L3VwbG9hZC9JbnZlbnRhcmlvUHJlZGljdGl2by9jbGFzc19kaWFncmFt.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvZ2h3cmZqOTdVNkZDU2NhUjJNM1pNcy9zYW5kYm94L0hMWWNZTVVFak1DQnYyUUYwdFZJVDctaW1hZ2VzXzE3NTM0NTkxODI3MTVfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwzVndiRzloWkM5SmJuWmxiblJoY21sdlVISmxaR2xqZEdsMmJ5OWpiR0Z6YzE5a2FXRm5jbUZ0LnBuZyIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5ODc2MTYwMH19fV19&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=afM6yzvfe4nhpl1OAoiS2qw7TTLqO7tgS4-P3Lk6kmLPQFbq3Pv8tbb672kvKJFZwgAHzR2QGxb06zLJij~OjrILMjqFNOIAxbkovlwAjAd4Xpvp6xB-3grP6rM2ChKPX62YLZttZDSiP78W-JsC228LeMjUndQuBDskQt1rgtcw1UJaw2Sp6uWNUWcveY-5AEQCysADPNPs4tb29iPntU-9TAFNqnsI5YDKLiVEAf1R77D9scu6Z00cNZAZ53qwZAlkEoXx71fs7W8ivcJSFDzjOW5tv8mxc9ua2jOGTbrbsGd8vBsnpfBbQd4rqlOgPK5Bwf7QyFHNWveEcxXVFQ__)

# Diagrama Entidad-Relación (ERD)

```mermaid
erDiagram
    FARMACIA ||--o{ EMPLEADO : tiene
    FARMACIA ||--o{ MANAGER : tiene
    FARMACIA ||--o{ INVENTARIO_FARMACIA : posee
    FARMACIA ||--o{ COMPRA : realiza
    PRODUCTO ||--o{ INVENTARIO_FARMACIA : contiene
    PRODUCTO ||--o{ VENTA : vendido_en
    PRODUCTO ||--o{ COMPRA : comprado_en
    EMPLEADO ||--o{ VENTA : realiza
    
    FARMACIA {
        string nombre_farmacia PK
        string distrito
        string ciudad
        string pais
    }
    
    PRODUCTO {
        string product_id PK
        string nombre_producto
        string clase
        float precio_unitario
        date fecha_vencimiento
    }
    
    EMPLEADO {
        string dni PK
        string nombre
        string apellido
        string password
        boolean es_admin
        int farmacia FK
    }
    
    MANAGER {
        int id PK
        string nombre
        string apellido
        string password
        string email
        int farmacia FK
    }
    
    INVENTARIO_FARMACIA {
        int farmacia FK
        string producto FK
        int stock
        PK (farmacia, producto)
    }
    
    VENTA {
        int codigo_venta PK
        string producto FK
        string empleado FK
        int quantity
        int dia
        string month
        int year
        float sales
        float igv
        float total
        string moneda
        string estado
        string tipo_comp
    }
    
    COMPRA {
        int id PK
        int farmacia FK
        string producto FK
        string proveedor
        int cantidad
        date fecha_compra
        float precio_unitarioC
        float total_compra
    }

## Instalación y Configuración

Para poner en marcha el proyecto en tu entorno local, sigue los siguientes pasos:

1.  **Clonar el Repositorio**:
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd InventarioPredictivo
    ```

2.  **Crear y Activar un Entorno Virtual** (Recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Linux/macOS
    # venv\Scripts\activate   # En Windows
    ```

3.  **Instalar Dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar la Base de Datos**:
    Por defecto, Django utiliza SQLite. No se requiere configuración adicional si usas SQLite. Si deseas usar otra base de datos (PostgreSQL, MySQL), edita `farmaciaPredictiva_project/settings.py`.

5.  **Aplicar Migraciones de la Base de Datos**:
    ```bash
    python manage.py makemigrations farmacia_app
    python manage.py migrate
    ```

6.  **Crear un Superusuario** (para acceder al panel de administración de Django):
    ```bash
    python manage.py createsuperuser
    ```
    Sigue las instrucciones para crear el usuario.

7.  **Ejecutar el Servidor de Desarrollo**:
    ```bash
    python manage.py runserver
    ```
    El sistema estará disponible en `http://127.0.0.1:8000/`.

## Uso del Sistema

Una vez que el servidor esté en funcionamiento, puedes acceder al sistema a través de tu navegador web. Utiliza las credenciales del superusuario o de los usuarios de prueba que hayas creado para iniciar sesión.

-   **Login**: Accede a `http://127.0.0.1:8000/login/`
-   **Dashboard (Manager/Admin)**: `http://127.0.0.1:8000/dashboard/`
-   **Dashboard (Empleado)**: `http://127.0.0.1:8000/empleado_dashboard/`
-   **Panel de Administración de Django**: `http://127.0.0.1:8000/admin/`

Explora las diferentes secciones para gestionar productos, registrar compras, ver ventas y acceder a las funcionalidades de predicción.

## Pruebas

El proyecto incluye un conjunto robusto de pruebas para asegurar la calidad y el correcto funcionamiento de la aplicación. Para obtener información detallada sobre cómo ejecutar e interpretar las pruebas, consulta el documento:

-   [Documentación de Uso de las Pruebas](documentacion_uso_pruebas.md)

## Posibles Errores y Soluciones

Si encuentras algún problema o error al usar o desarrollar el sistema, consulta el siguiente documento para obtener soluciones a problemas comunes:

-   [Posibles Errores y Soluciones](documentacion_posibles_errores.md)

## Contribución

¡Las contribuciones son bienvenidas! Si deseas contribuir a este proyecto, por favor, sigue estos pasos:

1.  Haz un fork del repositorio.
2.  Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3.  Realiza tus cambios y asegúrate de que las pruebas pasen.
4.  Escribe nuevas pruebas para tus cambios si es necesario.
5.  Haz commit de tus cambios (`git commit -m 'feat: Añadir nueva funcionalidad X'`).
6.  Sube tus cambios a tu fork (`git push origin feature/nueva-funcionalidad`).
7.  Abre un Pull Request explicando tus cambios.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.


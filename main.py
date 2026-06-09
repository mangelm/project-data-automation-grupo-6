from src.sakila_ETL import generar_reporte_csv
import platform
import subprocess
import os

# Definimos las 3 consultas
SQL_CLIENTES = """SELECT 
    -- Estandarización a minúsculas
    LOWER(c.first_name) AS first_name,
    LOWER(c.last_name) AS last_name,
    LOWER(c.email) AS email,
    LOWER(ci.city) AS city,
    
    -- Datos del alquiler y pago
    r.rental_id,
    r.rental_date,
    r.return_date,
    p.payment_id,
    p.amount,
    
    -- Columna derivada: Duración en días
    DATEDIFF(r.return_date, r.rental_date) AS rental_duration
-- Tabla principal: rental, que contiene la información de los alquileres
FROM rental r

-- Joins definidos por llaves primarias/foráneas
-- Se unen las tablas rental, payment, customer, address y city para obtener toda la información relevante
INNER JOIN payment p ON r.rental_id = p.rental_id
INNER JOIN customer c ON r.customer_id = c.customer_id
INNER JOIN address a ON c.address_id = a.address_id
INNER JOIN city ci ON a.city_id = ci.city_id

-- Filtros de limpieza y consistencia lógica
WHERE 
    -- Filtros de limpieza solicitados
    r.rental_id IS NOT NULL 
    AND p.payment_id IS NOT NULL
    -- Asegurar que el monto del pago sea positivo
    AND p.amount > 0
    AND r.return_date IS NOT NULL
    -- Consistencia lógica de fechas
    AND r.rental_date < r.return_date"""
SQL_CATALOGO = """
SELECT 
        f.film_id,
        LOWER(TRIM(f.title)) AS title,
        LOWER(TRIM(f.description)) AS description,
        f.release_year,
        LOWER(l.name) AS language,
        LOWER(cat.name) AS category,
        f.length,
        f.rating,
        -- Columna derivada: Película larga
        CASE WHEN f.length >= 120 THEN 1 ELSE 0 END AS is_long_film,
        -- Conteo de copias en inventario (Agrupación útil)
        (SELECT COUNT(*) FROM inventory i WHERE i.film_id = f.film_id) AS inventory_count
    FROM film f
    INNER JOIN language l ON f.language_id = l.language_id
    LEFT JOIN film_category fc ON f.film_id = fc.film_id
    LEFT JOIN category cat ON fc.category_id = cat.category_id
    WHERE 
        f.length > 0              -- Eliminar duraciones <= 0
        AND f.rating IS NOT NULL   -- Eliminar ratings nulos
        AND f.title IS NOT NULL   -- Integridad básica"""
SQL_ACTORES =  """
SELECT 
    f.film_id,
    f.title AS titulo_pelicula,
    a.actor_id,
    CONCAT(LOWER(a.first_name), ' ', LOWER(a.last_name)) AS actor_full_name,
    -- Conteo de actores en esta película específica
    (SELECT COUNT(*) 
        FROM film_actor fa2 
        WHERE fa2.film_id = f.film_id) AS total_actores_en_pelicula,
    -- Conteo de películas en las que participa este actor
    (SELECT COUNT(*) 
        FROM film_actor fa3 
        WHERE fa3.actor_id = a.actor_id) AS total_peliculas_del_actor
FROM film f
INNER JOIN film_actor fa ON f.film_id = fa.film_id
INNER JOIN actor a ON fa.actor_id = a.actor_id
ORDER BY f.title ASC # Tu tercera query"""

def run():
    print("Iniciando extracción de reportes...")
    
    # Ejecutamos la función 3 veces para obtener los 3 CSVs independientes
    generar_reporte_csv(SQL_CLIENTES, "actividad_clientes")
    generar_reporte_csv(SQL_CATALOGO, "catalogo_peliculas")
    generar_reporte_csv(SQL_ACTORES, "elenco_popularidad")
    abrir_dashboard()
    
    print("¡Todos los archivos han sido generados en la carpeta /outputs!")

def abrir_dashboard():
    """
    Busca y abre el archivo Excel del Dashboard en la carpeta especificada.
    """
    # Construimos la ruta relativa al archivo
    # Asumiendo que el script se ejecuta desde la raíz del proyecto
    ruta_archivo = os.path.join("dashboard", "Sakila_Dashboard.xlsx")

    # Verificamos si el archivo existe para evitar errores de sistema
    if os.path.exists(ruta_archivo):
        print(f"Abriendo {ruta_archivo}...")
        
        # Detectamos el sistema operativo para usar el comando correcto
        sistema = platform.system()
        
        if sistema == "Windows":
            os.startfile(ruta_archivo)
        elif sistema == "Darwin":  # macOS
            subprocess.call(["open", ruta_archivo])
        else:  # Linux
            subprocess.call(["xdg-open", ruta_archivo])
    else:
        print(f"Error: No se encontró el archivo en {ruta_archivo}")
        print("Asegúrate de que la carpeta 'dashboard' y el archivo existen.")

if __name__ == "__main__":
    run()
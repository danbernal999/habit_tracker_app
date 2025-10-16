"""
Script para generar un archivo Excel de ejemplo para probar el cargador masivo.
Ejecuta este script para crear un archivo 'datos_ejemplo.xlsx' con datos de prueba.
"""

import pandas as pd
from datetime import datetime

# Creo datos de ejemplo
data = {
    'Nombre': ['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez', 'Luis Rodríguez',
               'Carmen Sánchez', 'José Fernández', 'Laura González', 'Miguel Torres', 'Isabel Ramírez'],
    'Email': ['juan@example.com', 'maria@example.com', 'carlos@example.com', 'ana@example.com', 'luis@example.com',
              'carmen@example.com', 'jose@example.com', 'laura@example.com', 'miguel@example.com', 'isabel@example.com'],
    'Edad': [25, 30, 35, 28, 42, 31, 29, 26, 38, 33],
    'Ciudad': ['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Bilbao',
               'Málaga', 'Zaragoza', 'Murcia', 'Palma', 'Las Palmas'],
    'Teléfono': ['600111222', '600222333', '600333444', '600444555', '600555666',
                 '600666777', '600777888', '600888999', '600999000', '600000111']
}

# Creo un DataFrame con pandas
df = pd.DataFrame(data)

# Guardo el DataFrame en un archivo Excel
filename = 'datos_ejemplo.xlsx'
df.to_excel(filename, index=False, engine='openpyxl')

print(f"✅ Archivo '{filename}' creado exitosamente con {len(df)} filas")
print(f"📊 Columnas: {', '.join(df.columns)}")
print(f"\nPuedes usar este archivo para probar el cargador masivo de Excel")
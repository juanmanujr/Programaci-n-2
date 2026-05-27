import os
import django
from datetime import datetime
from django.apps import apps

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_ventas.settings')
django.setup()

def generar_reporte_html():
    # Obtener todos los modelos
    modelos = apps.get_models()
    
    # Filtrar solo los modelos de tu app
    mis_modelos = []
    for modelo in modelos:
        nombre_app = modelo._meta.app_label
        if nombre_app not in ['admin', 'auth', 'contenttypes', 'sessions']:
            mis_modelos.append(modelo)
    
    total_modelos = len(mis_modelos)
    
    # HTML simple
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Reporte de {total_modelos} Tablas - SISVENTAS</title>
    <style>
        body {{ font-family: Arial; margin: 30px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: auto; background: white; padding: 20px; border-radius: 10px; }}
        h1 {{ color: #2c3e50; }}
        .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .table th {{ background: #3498db; color: white; padding: 10px; }}
        .table td {{ border: 1px solid #ddd; padding: 8px; }}
        .table tr:nth-child(even) {{ background: #f9f9f9; }}
    </style>
</head>
<body>
    <div class="container">
        <h1> REPORTE DE {total_modelos} TABLAS - SISVENTAS</h1>
        <p><strong>Alumno:</strong> Juan Manuel Gómez Achucarro</p>
        <p><strong>Materia:</strong> Programación 2 - Parcial 2</p>
        <p><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y')}</p>
        
        <table class="table">
            <tr><th>#</th><th>Nombre del Modelo</th><th>Tabla en BD</th></tr>'''
    
    for i, modelo in enumerate(sorted(mis_modelos, key=lambda m: m.__name__), 1):
        html += f'''<tr>
            <td>{i}</td>
            <td><strong>{modelo.__name__}</strong></td>
            <td><code>{modelo._meta.db_table}</code></td>
        </tr>'''
    
    html += f'''</table>
        <p><strong>Total:</strong> {total_modelos} modelos implementados</p>
        <p><strong>Verificar:</strong> Ejecutar EJECUTAR_DIRECTO.bat y abrir http://127.0.0.1:8000/admin/</p>
    </div>
</body>
</html>'''
    
    # Guardar
    with open('reporte_tablas.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f" Reporte generado: reporte_tablas.html")
    print(f" Total de modelos: {total_modelos}")
    
    # Mostrar en consola
    print("\n LISTA DE MODELOS:")
    for i, modelo in enumerate(sorted(mis_modelos, key=lambda m: m.__name__), 1):
        print(f"{i:3}. {modelo.__name__}")
    
    return total_modelos

if __name__ == "__main__":
    generar_reporte_html()

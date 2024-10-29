import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta

# URL del calendario
url = "https://portales.uloyola.es/LoyolaHorario/horario.xhtml?curso=2024%2F25&tipo=M&titu=551&campus=2&ncurso=2&grupo=A"

# Obtener el contenido de la página
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Aquí debes ajustar las clases o etiquetas para encontrar los datos específicos.
# Por ejemplo:
horarios = []
for item in soup.find_all("div", class_="nombre-clase"):  # Cambia "nombre-clase" al nombre real de la clase HTML que contiene la información.
    nombre_clase = item.text.strip()
    fecha = item.find_next("div", class_="fecha").text.strip()  # Ajusta aquí
    hora_inicio = item.find_next("div", class_="hora-inicio").text.strip()  # Ajusta aquí
    hora_fin = item.find_next("div", class_="hora-fin").text.strip()  # Ajusta aquí
    
    horarios.append({
        "nombre_clase": nombre_clase,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin
    })

# Paso 2: Convertir los datos a eventos de iCalendar
cal = Calendar()

for horario in horarios:
    # Parsear fecha y hora
    fecha = datetime.strptime(horario["fecha"], "%d/%m/%Y")
    hora_inicio = datetime.strptime(horario["hora_inicio"], "%H:%M").time()
    hora_fin = datetime.strptime(horario["hora_fin"], "%H:%M").time()
    
    # Crear evento
    event = Event()
    event.name = horario["nombre_clase"]
    event.begin = datetime.combine(fecha, hora_inicio)
    event.end = datetime.combine(fecha, hora_fin)
    cal.events.add(event)

# Paso 3: Guardar el archivo .ics
with open("calendario.ics", "w") as my_file:
    my_file.writelines(cal.serialize_iter())

print("Archivo de calendario guardado como 'calendario.ics'")

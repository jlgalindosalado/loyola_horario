import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from ics import Calendar, Event
import pytz

# URL to request
url = 'https://portales.uloyola.es/LoyolaHorario/horario.xhtml?curso=2024%2F25&tipo=M&titu=551&campus=2&ncurso=2&grupo=A'


def get_json():
    # Send the GET request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all <script> tags with type="text/javascript"
        script_tags = soup.find_all('script', type='text/javascript')
        
        # Initialize a variable to store the desired function content
        render_horario_js_content = None

        # Iterate through script tags to find the one containing `renderHorarioJs`
        for script in script_tags:
            if 'function renderHorarioJs' in (script.string or ''):
                render_horario_js_content = script.string
                break  # Stop after finding the first occurrence

        # If the function was found, search for `eventos_calendario`
        if render_horario_js_content:
            # Find the variable definition
            eventos_calendario_match = re.search(r'var eventos_calendario = (\[.*?\]);', render_horario_js_content, re.DOTALL)
            
            if eventos_calendario_match:
                # Extract the JSON-like content
                eventos_calendario_content = eventos_calendario_match.group(1)

                # Parse the content to validate it's proper JSON
                try:
                    eventos_calendario_json = json.loads(eventos_calendario_content)

                    # Save it to a JSON file
                    with open('eventos_calendario.json', 'w', encoding='utf-8') as file:
                        json.dump(eventos_calendario_json, file, ensure_ascii=False, indent=4)
                    print("Variable 'eventos_calendario' saved to 'eventos_calendario.json'.")
                except json.JSONDecodeError:
                    print("Error: The content of eventos_calendario is not valid JSON.")
            else:
                print("Variable 'eventos_calendario' not found in the script content.")
        else:
            print("No <script> tag containing 'renderHorarioJs' found in the response.")
    else:
        print(f"Failed to retrieve the content. Status code: {response.status_code}")


# Load the JSON data
def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Create an iCalendar file
def create_ics():
    # Load the JSON data
    with open('eventos_calendario.json', 'r', encoding='utf-8') as file:
        events_data = json.load(file)

    # Create a calendar
    calendar = Calendar()

    # Loop through each event in JSON data and add it to the calendar
    for item in events_data:
        event = Event()
        event.name = item.get('title', 'No Title')  # Default title if missing
        
        # Handle 'start' and 'end' times, if available
        start_time = item.get('start')
        end_time = item.get('end')
        
        # Only set the event's start and end times if they are present
        if start_time:
            event.begin = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        if end_time:
            event.end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

        # Optional fields
        event.description = item.get('extendedProps', {}).get('descripcion', '')
        location_info = item.get('title', '').split("Aula: ")
        event.location = location_info[-1].strip() if len(location_info) > 1 else 'No Location'
        
        calendar.events.add(event)

    # Save the calendar to a .ics file
    with open('calendario.ics', 'w', encoding='utf-8') as f:
        f.writelines(calendar)

    print("ICS file created successfully!")

events = load_json("eventos_calendario.json")
create_ics()
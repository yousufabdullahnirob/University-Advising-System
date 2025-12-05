import os
import django
import re
import pdfplumber
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advising_system.settings')
django.setup()

from advising_app.models import Course

def parse_time(time_str):
    # Format: 08:30 AM - 10:00 AM
    try:
        start_str, end_str = time_str.split(' - ')
        start_time = datetime.strptime(start_str, '%I:%M %p').time()
        end_time = datetime.strptime(end_str, '%I:%M %p').time()
        return start_time, end_time
    except ValueError:
        return None, None

def map_day(day_code):
    mapping = {
        'S': 'Sun',
        'M': 'Mon',
        'T': 'Tue',
        'W': 'Wed',
        'R': 'Thu',
        'F': 'Fri',
        'A': 'Sat',
        'ST': 'Sun', # Assuming ST might be Sunday-Tuesday or similar, but for single char mapping:
        'MW': 'Mon', # If combined, we might need to handle multiple entries. 
                     # But the model has a single 'day' field. 
                     # If a course is on multiple days, usually it's listed twice or we need to change the model.
                     # For now, I'll map the first letter or common codes.
    }
    # If the code is multiple characters (e.g. ST), we might need to create multiple course entries or handle it.
    # Given the model has 'day' as a single choice, I'll just take the first valid mapping or default to Mon.
    # Let's assume the PDF has single day per row for now based on the snippet "S".
    return mapping.get(day_code, 'Mon')

def import_courses(pdf_path):
    # Regex to capture: Code, Section, Faculty, Capacity, Day, Time, Room
    # Example: CSE101 2 AT 0/30 S 08:30 AM - 10:00 AM 217
    # Regex: (Code) (Section) (Faculty) (Cap) (Day) (Time) (Room)
    line_re = re.compile(r"^([A-Z]{3}\d{3})\s+(\d+)\s+([A-Z]+)\s+\d+/\d*\s+([A-Z]+)\s+(\d{2}:\d{2} [AP]M - \d{2}:\d{2} [AP]M)\s+(.+)$")

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            for line in text.split('\n'):
                match = line_re.match(line.strip())
                if match:
                    code, section, faculty_initials, day_code, time_range, room = match.groups()
                    
                    start_time, end_time = parse_time(time_range)
                    if not start_time:
                        continue

                    day = map_day(day_code)
                    
                    # Create or update course
                    # Note: We don't have title or credit in this line. 
                    # We might need to fetch it from existing courses or set defaults.
                    # Since we are importing, maybe we assume the course code exists or we set dummy values?
                    # The user said "take course time section and room". 
                    # If I create a new course, I need title and credit.
                    # I'll try to find an existing course with the same code (ignoring section) to copy title/credit,
                    # or set defaults if not found.
                    
                    existing_course = Course.objects.filter(code=code).first()
                    title = existing_course.title if existing_course else f"Course {code}"
                    credit = existing_course.credit if existing_course else 3.0
                    department = existing_course.department if existing_course else "CSE" # Default

                    course, created = Course.objects.update_or_create(
                        code=code,
                        section=section,
                        defaults={
                            'title': title,
                            'credit': credit,
                            'department': department,
                            'day': day,
                            'start_time': start_time,
                            'end_time': end_time,
                            'room': room,
                            # 'assigned_faculty': None # We can't easily link faculty initials
                        }
                    )
                    action = "Created" if created else "Updated"
                    print(f"{action}: {code} Sec {section} {day} {time_range} Room {room}")
                else:
                    # print(f"Skipped: {line}") # Uncomment to debug
                    pass

if __name__ == "__main__":
    import_courses('faculty_list.pdf')

from datetime import datetime

def format_deadline(date_value):
    """
    Formats a date into DD/MM/YYYY format.
    Accepts strings or datetime.date/datetime.datetime objects.
    """
    if not date_value:
        return None
    if isinstance(date_value, str):
        try:
            # Try Odoo default format
            parsed_date = datetime.strptime(date_value, "%Y-%m-%d")
        except ValueError:
            try:
                # Try full datetime format
                parsed_date = datetime.strptime(date_value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return date_value  # Return as-is if parsing fails
    else:
        parsed_date = date_value
    return parsed_date.strftime("%d/%m/%Y")


def map_job_fields(job, source='odoo'):
    """
    Map job fields from Odoo or local DB to a unified format.
    """
    if source == 'odoo':
        return {
            'id': job.get('id'),
            'name': job.get('name'),
            'job_description': job.get('job_description', ''),
            'career_level': job.get('career_level', 'Not Specified'),
            'cgpa_requirement': job.get('cgpa_requirement', 0.0),
            'deadline': format_deadline(job.get('deadline')),
            'location': job.get('location'),
            'address_id': job.get('address_id')
        }
    elif source == 'local':
        return {
            'id': job.get('id'),
            'name': job.get('job_title'),
            'job_description': job.get('job_description', ''),
            'career_level': job.get('level', 'Not Specified'),
            'cgpa_requirement': 0.0,
            'deadline': format_deadline(job.get('job_deadline')),
            'location': job.get('location'),
            'address_id': False
        }
    else:
        raise ValueError("Unknown job source")

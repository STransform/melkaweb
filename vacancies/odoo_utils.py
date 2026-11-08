import xmlrpc.client
from decouple import config

def get_odoo_connection():
    ODOO_URL = config('ODOO_URL', default='http://172.10.12.208:3334')
    ODOO_DB = config('ODOO_DB', default='otech_testing')
    ODOO_USERNAME = config('ODOO_USERNAME', default='admin')
    ODOO_PASSWORD = config('ODOO_PASSWORD', default='admin')

    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        version = common.version()
        if not version:
            raise Exception("Failed to connect to Odoo server.")
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if not uid:
            raise Exception("Odoo authentication failed. Check database, username, or password.")
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        return models, ODOO_DB, uid, ODOO_PASSWORD
    except ConnectionRefusedError:
        raise Exception(f"Connection refused to {ODOO_URL}. Ensure Odoo server is running on port 3334.")
    except Exception as e:
        raise Exception(f"Error connecting to Odoo: {str(e)}")

def fetch_odoo_jobs(search=None, offset=0, limit=12):
    try:
        models, db, uid, password = get_odoo_connection()
        domain = [('is_published', '=', True), ('website_published', '=', True)]
        if search:
            domain.append(('name', 'ilike', search))
        job_ids = models.execute_kw(db, uid, password, 'hr.job', 'search', [domain], {
            'offset': offset,
            'limit': limit,
            'order': 'create_date desc'  # Sort by create_date descending
        })
        if not job_ids:
            pass

        jobs_data = models.execute_kw(db, uid, password, 'hr.job', 'read', 
            [job_ids, ['id', 'name', 'description', 'career_level', 'cgpa_requirement', 'deadline', 'company_id']])
        
        jobs = []
        for job in jobs_data:
            try:
                job_entry = {
                    'id': job['id'],
                    'name': job['name'],
                    'job_title': job['name'],
                    'job_description': job.get('description', '') or '',
                    'career_level': job.get('career_level', 'Not Specified') or 'Not Specified',
                    'cgpa_requirement': job.get('cgpa_requirement', 0.0) or 0.0,
                    'date_to': job.get('deadline', '') or '',
                    'company_id': job.get('company_id', False),
                    'address_id': False,
                    'department_id': False,
                    'recruitment_request_id': False
                }
                jobs.append(job_entry)
            except Exception as e:
                continue

        return jobs
    except Exception as e:
        return []

def create_odoo_application(vals):
    try:
        models, db, uid, password = get_odoo_connection()
        
        # Check hr.candidate fields for debugging
        candidate_fields = models.execute_kw(db, uid, password, 'ir.model.fields', 'search_read',
                                            [[('model', '=', 'hr.candidate')]], {'fields': ['name', 'ttype', 'required']})
        required_fields = [f.name for f in candidate_fields if f['required']]

        # Create res.partner record
        partner_data = {
            'name': vals['partner_name'],
            'email': vals.get('email_from', ''),
            'phone': vals.get('partner_phone', ''),
            'company_id': vals.get('company_id', False),
        }
        partner_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [partner_data])
        vals['partner_id'] = partner_id

        # Create hr.candidate record
        candidate_data = {
            'partner_name': vals['partner_name'],
            'email_from': vals.get('email_from', ''),
            'partner_phone': vals.get('partner_phone', ''),
            'company_id': vals.get('company_id', False),
            'partner_id': partner_id,
        }
        # Include required fields if missing
        for field in required_fields:
            if field not in candidate_data:
                if field in ['partner_name', 'email_from', 'partner_phone', 'company_id', 'partner_id']:
                    continue
                candidate_data[field] = False
        candidate_id = models.execute_kw(db, uid, password, 'hr.candidate', 'create', [candidate_data])
        vals['candidate_id'] = candidate_id

        # Handle CV attachment
        attachment = None
        if 'cv_data' in vals:
            attachment = {
                'name': vals['cv_filename'],
                'datas': vals['cv_data'],
                'res_model': 'hr.applicant',
                'res_id': 0,
                'public': True
            }
            attachment_id = models.execute_kw(db, uid, password, 'ir.attachment', 'create', [attachment])
            vals['attachment_ids'] = [(4, attachment_id)]
            del vals['cv_data'], vals['cv_filename']
        
        # Set initial stage
        initial_stage = models.execute_kw(db, uid, password, 'hr.recruitment.stage', 'search',
                                         [[('name', '=', 'Initial Qualification')]], {'limit': 1})
        if initial_stage:
            vals['stage_id'] = initial_stage[0]

        # Remove invalid fields
        if 'company_id' in vals and not vals['company_id']:
            del vals['company_id']
        if 'department_id' in vals:
            del vals['department_id']

        applicant_id = models.execute_kw(db, uid, password, 'hr.applicant', 'create', [vals])
        return applicant_id
    except xmlrpc.client.Fault as e:
        raise Exception(f"Error: {e.faultString}")
    except Exception as e:
        raise
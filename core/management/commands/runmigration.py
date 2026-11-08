import subprocess
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from accounts.models import UserProfile

from core.models import Pages

class Command(BaseCommand):
    help = 'Runs both makemigrations and migrate commands at once and updates the db if there is anything to update.'
        
    def add_arguments(self, parser):
        parser.add_argument('--populate_data', type=bool, help='Use like --populate_data=True, to populate initial data like Page controller obj and Site name.', default=False)

    def delete_default_permissions(self):
        # Delete unnecessary permission objects 
        default_custom_apps = ["about_us","accounts","blogs","core","dashboard", "documents","news","vacancies"]
        required_apps = getattr(settings,"CUSTOM_INSTALLED_APPS",default_custom_apps) 
        required_apps.append("auth")

        all_perms = Permission.objects.all() 
        # print(all_perms.count())
        for p in all_perms:
            app = str(p.content_type).split("|")[0].strip()
            if app not in required_apps:
                p.delete()
        # print(Permission.objects.count())
        
    def data_migrator(self):
        print("Populating initial data...\n")

        # creating superuser
        User = get_user_model()
        email = "adminuser@gmail.com"
        pw = "Mofed@24"
        if UserProfile.objects.filter(email =email):
            self.stdout.write(self.style.WARNING(f'Superuser with an email {email} already exists. Skipping creation.'))
        else:
            try:# Create the superuser with default values
                User.objects.create_superuser(email=email, password=pw,first_name="Superadmin", last_name="User")
                self.stdout.write(self.style.SUCCESS(f'Successfully created superuser with email ={email} & pw = {pw}.'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error creating superuser: {e}'))
            
        try:#Create site name
            site = Site.objects.first()
            if not site:
                site = Site.objects.create(domain="bureauoffinance.com", name="Bureau of Finance")
                print("Created a default site name of ",site.name, " and domain of ",site.domain,end="\n" )
            
            elif site.name == "otech.com":
                    site.name = "OTECH Engineering"
                    site.domain = "otech.com"
                    site.save()
                    print("Default site name updated to ",site.name, " and domain to ",site.domain,end="\n" )
                
        except Exception as e:
            print("Exception occurred while creating site name & domain : ",e)

        # check if pages are created
        if not Pages.objects.first() :
            Pages.objects.create()
            print("Created page controller setting object.\n")
        

        print("Data population completed")
        
    def handle(self, *args, **options):
        pop_data = options['populate_data']
        self.stdout.write("Making migrations to all apps...")
        call_command('makemigrations','about_us','accounts','blogs','core',
                     'dashboard','documents','news','vacancies','visit_counter', interactive=True)
        self.stdout.write(" \nMigrating...")
        call_command('migrate', interactive=True)
        self.stdout.write(self.style.SUCCESS("\nMigration completed successfully"))
        self.delete_default_permissions()
        # if want to populate data
        if pop_data:
            self.data_migrator()
        self.stdout.write("\nDB is updated.")



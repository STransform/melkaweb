"""Compile project translations using the existing polib dependency."""
from pathlib import Path

import polib
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Compile project locale catalogs without requiring system gettext tools.'

    def handle(self, *args, **options):
        for root in settings.LOCALE_PATHS:
            for source in Path(root).glob('*/LC_MESSAGES/*.po'):
                target = source.with_suffix('.mo')
                polib.pofile(str(source)).save_as_mofile(str(target))
                self.stdout.write(f'Compiled {source.relative_to(settings.BASE_DIR)}')

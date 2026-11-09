from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('dashboard', '0001_initial')]

    operations = [
        migrations.AlterField(
            model_name='featuredwork',
            name='background_image',
            field=models.ImageField(
                blank=True,
                upload_to='featured_work_backgrounds/',
                help_text='Optional. Recommended image size: 720 × 400.',
            ),
        ),
    ]

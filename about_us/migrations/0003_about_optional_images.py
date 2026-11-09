from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('about_us', '0002_initial')]

    operations = [
        migrations.AlterField(
            model_name='about',
            name=name,
            field=models.ImageField(
                blank=True,
                upload_to='about_images/',
                help_text='Optional. Recommended image size: 200 × 300.',
            ),
        )
        for name in ['image_one', 'image_two', 'image_three']
    ]

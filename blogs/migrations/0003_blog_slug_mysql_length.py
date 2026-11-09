from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('blogs', '0002_blog_author_bio_blog_content_format_blog_difficulty_and_more')]
    operations = [migrations.AlterField(
        model_name='blog', name='slug',
        field=models.SlugField(blank=True, unique=True, max_length=255, help_text='Generated on first save. Keep stable after sharing.'),
    )]

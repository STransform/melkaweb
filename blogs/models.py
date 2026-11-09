from django.db import models
from accounts.models import UserProfile as User
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse

class BlogCategory(models.Model):
    name = models.CharField(max_length=100,help_text="Make sure to submit a max of 100 characters.")
    def __str__(self):
        return self.name

    def get_list_fields():
        return ['name']
    list_fields = get_list_fields()
    
    
class Blog(models.Model):
    title = models.CharField(max_length=255,help_text="Make sure to submit a max of 255 characters.")
    blog_category = models.ForeignKey(BlogCategory, on_delete = models.SET_NULL, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    published_status = models.CharField(max_length=20, choices=[('Published', 'Published'), ('Hold', 'Draft')], default='Hold')
    content = models.TextField()
    images = models.ImageField(upload_to='blog_images/', blank=True, help_text='Optional cover image. Recommended: 1200 × 630.')
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text='Generated on first save. Keep stable after sharing.')
    summary = models.CharField(max_length=300, blank=True, help_text='A short introduction for cards and social previews.')
    content_format = models.CharField(max_length=12, choices=[('markdown', 'Markdown'), ('legacy', 'Existing HTML / text')], default='markdown')
    tags = models.CharField(max_length=250, blank=True, help_text='Comma-separated topics, e.g. Docker, Python, AWS.')
    difficulty = models.CharField(max_length=20, choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')], default='Beginner')
    prerequisites = models.TextField(blank=True, help_text='What readers should know or install before starting.')
    author_bio = models.TextField(blank=True, help_text='A short introduction to the author.')
    series = models.CharField(max_length=150, blank=True, help_text='Optional tutorial series name.')
    series_order = models.PositiveIntegerField(default=1)
    seo_description = models.CharField(max_length=160, blank=True)
    published_at = models.DateTimeField(null=True, blank=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    excluded_fields = ['slug']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:240] or 'tutorial'
            candidate, suffix = base, 2
            while Blog.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate, suffix = f'{base}-{suffix}', suffix + 1
            self.slug = candidate
        if self.published_status == 'Published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tutorial_detail', kwargs={'slug': self.slug})

    @property
    def reading_minutes(self):
        import re
        return max(1, (len(re.sub(r'<[^>]+>', '', self.content).split()) + 199) // 200)

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return self.title

    def comments(self):
        return self.comment_set.filter(approved = True)

    def get_list_fields():
        return ['title', 'blog_category','created_by','created_date','published_status', 'view_count', 'like_count', 'engaged_count']

    def view_count(self):
        return self.visits.count()

    def engaged_count(self):
        return self.visits.filter(engaged=True).count()

    def like_count(self):
        return self.likes.count()
    
    list_fields = get_list_fields()
    
    def category(self):
        return self.blog_category if self.blog_category else ""
    

class BlogComment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comment_set")
    author = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return f'Comment by {self.author} on {self.blog.title}'

    def get_list_fields():
        return ['blog', 'author', 'email', 'approved' ]
    
    list_fields = get_list_fields()


class BlogLike(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='likes')
    visitor = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['blog', 'visitor'], name='unique_blog_visitor_like')]


class BlogVisit(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='visits')
    visitor = models.CharField(max_length=64)
    day = models.DateField(default=timezone.localdate)
    source = models.CharField(max_length=80, blank=True)
    engaged = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['blog', 'visitor', 'day'], name='unique_blog_daily_visit')]
    



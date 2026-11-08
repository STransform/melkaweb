from django.db import models
from accounts.models import UserProfile as User

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
    published_status = models.CharField(max_length=20, choices=[('Published', 'Published'), ('Hold', 'Hold')])
    content = models.TextField()
    images = models.ImageField(upload_to='blog_images/',help_text="Make sure to submit an image of 500 X 300.")

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return self.title

    def comments(self):
        return self.comment_set.filter(approved = True)

    def get_list_fields():
        return ['title', 'blog_category','created_by','created_date','published_status' ]
    
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
    



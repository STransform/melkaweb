from django.db import models
from accounts.models import UserProfile as User

class NewsCategory(models.Model):
    name = models.CharField(max_length=100,help_text="Make sure to submit a max of 100 characters.")
    def __str__(self):
        return self.name
    
    def get_list_fields():
        return ['name']
    
    list_fields = get_list_fields()

class NewsArticle(models.Model):
    title = models.CharField(max_length=255,help_text="Make sure to submit a max of 255 characters.")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='news_images/',
                                       help_text="Make sure to submit an image of 400 X 300.")
    minutes_read = models.IntegerField()
    news_category = models.ForeignKey(NewsCategory, on_delete = models.SET_NULL, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-id',)
        
    def __str__(self):
        return self.title
    
    def category(self):
        return self.news_category if self.news_category else ""
    
    def get_list_fields():
        return ['title', 'created_by', 'minutes_read', 'news_category', 'created_at']
    
    list_fields = get_list_fields()

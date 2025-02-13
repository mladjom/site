from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .category import Category
from .tag import Tag
from .featured_image import FeaturedImageModel
from bs4 import BeautifulSoup

class PostManager(models.Manager):
    def active(self):
        return self.filter(status='published')

class Post(FeaturedImageModel, models.Model):
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('review', _('Under Review')),
        ('published', _('Published')),
    ]
    title = models.CharField(max_length=255, unique=True, verbose_name=_('Title'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Slug'))
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='posts', verbose_name=_('Author'))
    content = models.TextField(verbose_name=_('Content'))
    excerpt = models.TextField(blank=True, verbose_name=_('Excerpt'))
    summary = models.TextField(blank=True, verbose_name=_('Summary'))

    meta_title = models.CharField(max_length=200, blank=True, verbose_name=_('Meta Title'))
    meta_description = models.TextField(max_length=160, blank=True, verbose_name=_('Meta Description'))

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='posts', verbose_name=_('Category'))
    tags = models.ManyToManyField(Tag, related_name='posts', verbose_name=_('Tags'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name=_('Status'))
    is_featured = models.BooleanField(default=False, verbose_name=_('Is Featured'))
    view_count = models.PositiveIntegerField(default=0, editable=False, verbose_name=_('View Count'))

    objects = PostManager()

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        soup = BeautifulSoup(self.content, 'html.parser')
        self.content = soup.prettify()  # Prettify the HTML            
        super(Post, self).save(*args, **kwargs)

    # Important to implement
    def get_featured_image_url(self):
        """Returns the post's featured image, or the category's image if unavailable."""
        if self.featured_image:
            return self.featured_image.url
        elif self.category.featured_image:
            return self.category.featured_image.url
        return None  # Or return a default image URL
import os

from django.db import models
from newblog.categorias.models import Categoria
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image
from django.conf import settings


class Post(models.Model):
    titulo_post = models.CharField(max_length=255, verbose_name='Título')
    autor_post = models.ForeignKey(User,on_delete=models.DO_NOTHING,verbose_name='Autor')
    data_post = models.DateTimeField(default=timezone.now, verbose_name='Data')
    conteudo_post = models.TextField(verbose_name='Conteudo')
    excerto_post = models.TextField(verbose_name='Excerto')
    categoria_post = models.ForeignKey(Categoria,on_delete=models.DO_NOTHING, blank=True, null=True,verbose_name='Categoria')
    imagem_post = models.ImageField(upload_to='post_img/%Y/%m/%d', blank=True, null=True, verbose_name='Imagem')
    publicado_post = models.BooleanField(default=False, verbose_name='Publicado')


    def __str__(self):
        return self.titulo_post

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.imagem_post:
            self.resize_image(self.imagem_post.name, 800)
    
    @staticmethod
    def resize_image(img_name, new_width):
        image_path = os.path.join(settings.MEDIA_ROOT, img_name)
        img = Image.open(image_path)
        width, height = img.size
        new_height = round((new_width * height) / width)
        
        if width <= new_width:
            img.close()
            return
        new_img = img.resize((new_width,new_height), Image.ANTIALIAS)
        new_img.save(
            image_path,
            optimize=True,
            quality=60
        )
        new_img.close()

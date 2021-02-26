from django.contrib import messages
from django.db.models import Count, Case, When, Q
from django.shortcuts import redirect
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from .models import Post
from ..comentarios.forms import FormComentario
from ..comentarios.models import Comentario


class PostIndex(ListView):
    model = Post
    template_name = 'index.html'
    paginate_by = 6
    context_object_name = 'posts'
    
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('categoria_post')
        qs = qs.order_by('-id').filter(publicado_post=True)
        qs = qs.annotate(
            numero_comentarios=Count(
                Case(
                    When(comentario__publicado_comentario=True, then=1)
                )
            )
        )
        
        return qs

class PostBusca(PostIndex):
    template_name = 'post_busca.html'
    
    def get_queryset(self):
        qs = super().get_queryset()
        termo = self.request.GET.get('termo')
        qs = qs.filter(
            Q(titulo_post__icontains=termo)|
            Q(autor_post__first_name__iexact=termo)|
            Q(conteudo_post__icontains=termo)|
            Q(excerto_post__icontains=termo)|
            Q(categoria_post__nome_cat__iexact=termo)

        )
        
        return qs

class PostCategoria(PostIndex):
    template_name = 'post_categoria.html'
    
    def get_queryset(self):
        qs = super().get_queryset()
        categoria = self.kwargs.get('categoria',None)
        
        qs = qs.filter(categoria_post__nome_cat__iexact=categoria)
        
        return qs

class PostDetalhes(UpdateView):
    template_name = 'post_detalhes.html'
    model = Post
    form_class = FormComentario
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        post = self.get_object()
        comentarios = Comentario.objects.filter(publicado_comentario=True,
                                                post_comentario=post.id)
        contexto['comentarios'] = comentarios
        
        return contexto
    
    def form_valid(self, form):
        post = self.get_object()
        comentario = Comentario(**form.cleaned_data)
        comentario.post_comentario = post
        
        if self.request.user.is_authenticated:
            comentario.usuario_comentario = self.request.user
        
        comentario.save()
        messages.success(self.request,'Comentário enviado com sucesso')
        
        return redirect('post_detalhes', pk=post.id)

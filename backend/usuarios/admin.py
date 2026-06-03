from django.contrib import admin
from django.utils.html import format_html
from .models import Usuario, LoginIntento


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'nombre', 'correo', 'rol', 'estado', 'is_deleted_display', 'fecha_eliminacion')
    list_filter = ('rol', 'estado', 'is_deleted', 'fecha_eliminacion')
    search_fields = ('nombre', 'correo')
    readonly_fields = ('fecha_eliminacion',)
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'correo', 'rol', 'estado')
        }),
        ('Seguridad', {
            'fields': ('contrasena',)
        }),
        ('Estado de Eliminación', {
            'fields': ('is_deleted', 'fecha_eliminacion'),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        """Mostrar todos los usuarios incluyendo eliminados en el admin"""
        return Usuario.objects.all_including_deleted()
    
    def is_deleted_display(self, obj):
        """Muestra el estado de soft delete con color"""
        if obj.is_deleted:
            return format_html(
                '<span style="color: red; font-weight: bold;">✓ ELIMINADO</span>'
            )
        return format_html(
            '<span style="color: green; font-weight: bold;">✓ ACTIVO</span>'
        )
    is_deleted_display.short_description = 'Eliminado'
    
    def delete_model(self, request, obj):
        """Sobreescribe delete para usar soft delete"""
        obj.soft_delete()
    
    def delete_queryset(self, request, queryset):
        """Sobreescribe delete_queryset para usar soft delete"""
        for obj in queryset:
            obj.soft_delete()
    
    actions = ['restore_usuarios', 'soft_delete_usuarios']
    
    def soft_delete_usuarios(self, request, queryset):
        """Acción para eliminar usuarios (soft delete)"""
        count = 0
        for usuario in queryset.filter(is_deleted=False):
            usuario.soft_delete()
            count += 1
        self.message_user(request, f'{count} usuario(s) eliminado(s).')
    soft_delete_usuarios.short_description = 'Eliminar usuarios (soft delete)'
    
    def restore_usuarios(self, request, queryset):
        """Acción para restaurar usuarios eliminados"""
        count = 0
        for usuario in queryset.filter(is_deleted=True):
            usuario.restore()
            count += 1
        self.message_user(request, f'{count} usuario(s) restaurado(s).')
    restore_usuarios.short_description = 'Restaurar usuarios eliminados'


@admin.register(LoginIntento)
class LoginIntentoAdmin(admin.ModelAdmin):
    list_display = ('id_intento', 'correo', 'resultado', 'ip', 'fecha')
    list_filter = ('resultado', 'fecha')
    search_fields = ('correo', 'ip')
    readonly_fields = ('correo', 'resultado', 'ip', 'user_agent', 'fecha')
    
    def has_add_permission(self, request):
        """No permitir agregar intentos de login manualmente"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar intentos de login"""
        return False

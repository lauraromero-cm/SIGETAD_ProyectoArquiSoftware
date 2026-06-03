from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_loginintento'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='Soft delete: usuario marcado como eliminado'),
        ),
        migrations.AddField(
            model_name='usuario',
            name='fecha_eliminacion',
            field=models.DateTimeField(blank=True, null=True, help_text='Fecha y hora de eliminación'),
        ),
        migrations.AddIndex(
            model_name='usuario',
            index=models.Index(fields=['is_deleted', 'estado'], name='idx_usuario_deleted_estado'),
        ),
        migrations.AddIndex(
            model_name='usuario',
            index=models.Index(fields=['correo', 'is_deleted'], name='idx_usuario_correo_deleted'),
        ),
    ]

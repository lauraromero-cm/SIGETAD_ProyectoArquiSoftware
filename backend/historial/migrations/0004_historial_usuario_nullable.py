from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('historial', '0003_historial_postulacion_nullable'),
        ('usuarios', '0003_soft_delete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historial',
            name='id_usuario',
            field=models.ForeignKey(
                db_column='id_usuario',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='historial_registrado',
                to='usuarios.usuario',
            ),
        ),
    ]

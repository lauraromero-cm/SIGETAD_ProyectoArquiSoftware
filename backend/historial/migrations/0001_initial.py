import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [('postulaciones', '0001_initial'), ('usuarios', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='Historial',
            fields=[
                ('id_historial', models.BigAutoField(primary_key=True, serialize=False)),
                ('tipo', models.CharField(max_length=30)),
                ('descripcion', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('id_postulacion', models.ForeignKey(db_column='id_postulacion', on_delete=django.db.models.deletion.CASCADE, related_name='historial', to='postulaciones.postulacion')),
                ('id_usuario', models.ForeignKey(db_column='id_usuario', on_delete=django.db.models.deletion.PROTECT, related_name='historial_registrado', to='usuarios.usuario')),
            ],
            options={'db_table': 'historial', 'ordering': ['-fecha']},
        ),
    ]

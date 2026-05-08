import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [('postulaciones', '0001_initial'), ('usuarios', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='Evaluacion',
            fields=[
                ('id_evaluacion', models.BigAutoField(primary_key=True, serialize=False)),
                ('calificacion', models.IntegerField()),
                ('comentarios', models.TextField(blank=True)),
                ('id_postulacion', models.OneToOneField(db_column='id_postulacion', on_delete=django.db.models.deletion.CASCADE, related_name='evaluacion', to='postulaciones.postulacion')),
                ('id_usuario', models.ForeignKey(db_column='id_usuario', on_delete=django.db.models.deletion.PROTECT, related_name='evaluaciones', to='usuarios.usuario')),
            ],
            options={'db_table': 'evaluacion', 'ordering': ['-id_evaluacion']},
        ),
    ]

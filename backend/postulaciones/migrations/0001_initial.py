import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [('candidatos', '0001_initial'), ('vacantes', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='Postulacion',
            fields=[
                ('id_postulacion', models.BigAutoField(primary_key=True, serialize=False)),
                ('estado', models.CharField(choices=[('postulado', 'Postulado'), ('en_revision', 'En revisión'), ('entrevista', 'Entrevista'), ('evaluacion', 'Evaluación'), ('finalista', 'Finalista'), ('rechazado', 'Rechazado'), ('contratado', 'Contratado')], default='postulado', max_length=30)),
                ('fecha_postulacion', models.DateTimeField(auto_now_add=True)),
                ('notas', models.TextField(blank=True)),
                ('id_candidato', models.ForeignKey(db_column='id_candidato', on_delete=django.db.models.deletion.CASCADE, related_name='postulaciones', to='candidatos.candidato')),
                ('id_vacante', models.ForeignKey(db_column='id_vacante', on_delete=django.db.models.deletion.CASCADE, related_name='postulaciones', to='vacantes.vacante')),
            ],
            options={'db_table': 'postulacion', 'ordering': ['-fecha_postulacion']},
        ),
        migrations.AddConstraint(
            model_name='postulacion',
            constraint=models.UniqueConstraint(fields=('id_candidato', 'id_vacante'), name='unique_candidato_vacante'),
        ),
    ]

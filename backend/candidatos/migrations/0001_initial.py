import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [('usuarios', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='Candidato',
            fields=[
                ('id_candidato', models.BigAutoField(primary_key=True, serialize=False)),
                ('nombre_completo', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=100)),
                ('telefono', models.CharField(blank=True, max_length=20)),
                ('profesion', models.CharField(blank=True, max_length=100)),
                ('experiencia_anios', models.IntegerField(default=0)),
                ('cv', models.CharField(blank=True, max_length=255)),
                ('foto_perfil', models.CharField(blank=True, max_length=255)),
                ('id_usuario', models.OneToOneField(db_column='id_usuario', on_delete=django.db.models.deletion.CASCADE, related_name='candidato', to='usuarios.usuario')),
            ],
            options={'db_table': 'candidato', 'ordering': ['id_candidato']},
        ),
    ]

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginIntento',
            fields=[
                ('id_intento', models.BigAutoField(primary_key=True, serialize=False)),
                ('correo', models.EmailField(max_length=100)),
                ('resultado', models.CharField(choices=[('exito', 'Éxito'), ('fallido', 'Fallido'), ('bloqueado', 'Bloqueado')], max_length=20)),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.CharField(blank=True, max_length=255)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('id_usuario', models.ForeignKey(blank=True, db_column='id_usuario', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='intentos_login', to='usuarios.usuario')),
            ],
            options={
                'db_table': 'login_intento',
                'ordering': ['-fecha'],
            },
        ),
        migrations.AddIndex(
            model_name='loginintento',
            index=models.Index(fields=['correo', '-fecha'], name='idx_login_correo_fecha'),
        ),
        migrations.AddIndex(
            model_name='loginintento',
            index=models.Index(fields=['resultado', '-fecha'], name='idx_login_result_fecha'),
        ),
    ]

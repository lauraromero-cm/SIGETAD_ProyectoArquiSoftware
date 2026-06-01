from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('historial', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    DO $$ BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'historial' AND column_name = 'cambios_detalles'
                        ) THEN
                            ALTER TABLE "historial" ADD COLUMN "cambios_detalles" jsonb DEFAULT '{}' NULL;
                        END IF;
                    END $$;
                    """,
                    reverse_sql='ALTER TABLE "historial" DROP COLUMN IF EXISTS "cambios_detalles";',
                ),
                migrations.RunSQL(
                    sql="""
                    DO $$ BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'historial' AND column_name = 'is_deleted'
                        ) THEN
                            ALTER TABLE "historial" ADD COLUMN "is_deleted" boolean DEFAULT false NOT NULL;
                        END IF;
                    END $$;
                    """,
                    reverse_sql='ALTER TABLE "historial" DROP COLUMN IF EXISTS "is_deleted";',
                ),
                migrations.RunSQL(
                    sql="""
                    DO $$ BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'historial' AND column_name = 'fecha_eliminacion'
                        ) THEN
                            ALTER TABLE "historial" ADD COLUMN "fecha_eliminacion" timestamp with time zone NULL;
                        END IF;
                    END $$;
                    """,
                    reverse_sql='ALTER TABLE "historial" DROP COLUMN IF EXISTS "fecha_eliminacion";',
                ),
                migrations.RunSQL(
                    sql="""
                    DO $$ BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'historial' AND column_name = 'id_entidad_tipo'
                        ) THEN
                            ALTER TABLE "historial" ADD COLUMN "id_entidad_tipo" varchar(50) DEFAULT 'postulacion' NOT NULL;
                        END IF;
                    END $$;
                    """,
                    reverse_sql='ALTER TABLE "historial" DROP COLUMN IF EXISTS "id_entidad_tipo";',
                ),
                migrations.RunSQL(
                    sql="""
                    DO $$ BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'historial' AND column_name = 'id_entidad_referencia'
                        ) THEN
                            ALTER TABLE "historial" ADD COLUMN "id_entidad_referencia" bigint NULL;
                        END IF;
                    END $$;
                    """,
                    reverse_sql='ALTER TABLE "historial" DROP COLUMN IF EXISTS "id_entidad_referencia";',
                ),
                migrations.RunSQL(
                    sql="""
                    DO $$ BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_hist_usuario_fecha') THEN
                            CREATE INDEX "idx_hist_usuario_fecha" ON "historial" ("id_usuario", "fecha" DESC);
                        END IF;
                    END $$;
                    """,
                    reverse_sql='DROP INDEX IF EXISTS "idx_hist_usuario_fecha";',
                ),
                migrations.RunSQL(
                    sql="""
                    DO $$ BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_hist_entidad_fecha') THEN
                            CREATE INDEX "idx_hist_entidad_fecha" ON "historial" ("id_entidad_tipo", "id_entidad_referencia", "fecha" DESC);
                        END IF;
                    END $$;
                    """,
                    reverse_sql='DROP INDEX IF EXISTS "idx_hist_entidad_fecha";',
                ),
                migrations.RunSQL(
                    sql="""
                    DO $$ BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_hist_tipo_fecha') THEN
                            CREATE INDEX "idx_hist_tipo_fecha" ON "historial" ("tipo", "fecha" DESC);
                        END IF;
                    END $$;
                    """,
                    reverse_sql='DROP INDEX IF EXISTS "idx_hist_tipo_fecha";',
                ),
                migrations.RunSQL(
                    sql="""
                    DO $$ BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.constraint_column_usage
                            WHERE table_name = 'historial' AND constraint_name = 'historial_immutable_check'
                        ) THEN
                            ALTER TABLE "historial" ADD CONSTRAINT "historial_immutable_check"
                            CHECK ("is_deleted" = false OR "fecha_eliminacion" IS NOT NULL);
                        END IF;
                    END $$;
                    """,
                    reverse_sql='ALTER TABLE "historial" DROP CONSTRAINT IF EXISTS "historial_immutable_check";',
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='historial',
                    name='tipo',
                    field=models.CharField(
                        choices=[
                            ('postulacion', 'Postulación'),
                            ('estado', 'Cambio de Estado'),
                            ('evaluacion', 'Evaluación'),
                            ('cambio_campo', 'Cambio de Campo'),
                            ('evento', 'Evento Manual'),
                        ],
                        max_length=30,
                    ),
                ),
                migrations.AddField(
                    model_name='historial',
                    name='cambios_detalles',
                    field=models.JSONField(
                        blank=True,
                        default=dict,
                        help_text='Detalles de cambios: {campo, valor_anterior, valor_nuevo}',
                        null=True,
                    ),
                ),
                migrations.AddField(
                    model_name='historial',
                    name='is_deleted',
                    field=models.BooleanField(default=False, help_text='Soft delete: no se elimina físicamente'),
                ),
                migrations.AddField(
                    model_name='historial',
                    name='fecha_eliminacion',
                    field=models.DateTimeField(blank=True, help_text='Fecha cuando se marcó como eliminado', null=True),
                ),
                migrations.AddField(
                    model_name='historial',
                    name='id_entidad_tipo',
                    field=models.CharField(
                        choices=[
                            ('postulacion', 'Postulación'),
                            ('vacante', 'Vacante'),
                            ('candidato', 'Candidato'),
                            ('usuario', 'Usuario'),
                            ('evaluacion', 'Evaluación'),
                        ],
                        default='postulacion',
                        help_text='Tipo de entidad que se audita',
                        max_length=50,
                    ),
                ),
                migrations.AddField(
                    model_name='historial',
                    name='id_entidad_referencia',
                    field=models.BigIntegerField(blank=True, help_text='ID de la entidad (ej: id_vacante, id_candidato)', null=True),
                ),
                migrations.AddIndex(
                    model_name='historial',
                    index=models.Index(fields=['id_usuario', '-fecha'], name='idx_hist_usuario_fecha'),
                ),
                migrations.AddIndex(
                    model_name='historial',
                    index=models.Index(fields=['id_entidad_tipo', 'id_entidad_referencia', '-fecha'], name='idx_hist_entidad_fecha'),
                ),
                migrations.AddIndex(
                    model_name='historial',
                    index=models.Index(fields=['tipo', '-fecha'], name='idx_hist_tipo_fecha'),
                ),
            ],
        ),
    ]

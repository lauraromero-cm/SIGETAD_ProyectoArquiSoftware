# Generated migration - columns already exist in database
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('historial', '0001_initial'),
    ]

    operations = [
        # Usar RunSQL para agregar columnas solo si no existen
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
            reverse_sql="ALTER TABLE historial DROP COLUMN IF EXISTS cambios_detalles;"
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
            reverse_sql="ALTER TABLE historial DROP COLUMN IF EXISTS is_deleted;"
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
            reverse_sql="ALTER TABLE historial DROP COLUMN IF EXISTS fecha_eliminacion;"
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
            reverse_sql="ALTER TABLE historial DROP COLUMN IF EXISTS id_entidad_tipo;"
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
            reverse_sql="ALTER TABLE historial DROP COLUMN IF EXISTS id_entidad_referencia;"
        ),
        
        # Agregar índices si no existen
        migrations.RunSQL(
            sql="""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_hist_usuario_fecha') THEN
                    CREATE INDEX idx_hist_usuario_fecha ON "historial" (id_usuario, -fecha);
                END IF;
            END $$;
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_hist_usuario_fecha;"
        ),
        
        migrations.RunSQL(
            sql="""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_hist_entidad_fecha') THEN
                    CREATE INDEX idx_hist_entidad_fecha ON "historial" (id_entidad_tipo, id_entidad_referencia, -fecha);
                END IF;
            END $$;
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_hist_entidad_fecha;"
        ),
        
        migrations.RunSQL(
            sql="""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_hist_tipo_fecha') THEN
                    CREATE INDEX idx_hist_tipo_fecha ON "historial" (tipo, -fecha);
                END IF;
            END $$;
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_hist_tipo_fecha;"
        ),
        
        # Agregar CHECK constraint si no existe
        migrations.RunSQL(
            sql="""
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.constraint_column_usage
                    WHERE table_name = 'historial' AND constraint_name = 'historial_immutable_check'
                ) THEN
                    ALTER TABLE "historial" ADD CONSTRAINT historial_immutable_check 
                    CHECK (is_deleted = false OR fecha_eliminacion IS NOT NULL);
                END IF;
            END $$;
            """,
            reverse_sql="ALTER TABLE historial DROP CONSTRAINT IF EXISTS historial_immutable_check;"
        ),
    ]

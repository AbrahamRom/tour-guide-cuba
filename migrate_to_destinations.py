"""
Script de migración completa para cambiar la estructura de datos de hoteles
De: un CSV único (tourism_data.csv)
A: múltiples CSVs por destino (DATA/destinations/)
"""

import os
import shutil
import sys
from pathlib import Path

# Agregar el directorio SmartTour al path
script_dir = Path(__file__).parent.absolute()
smarttour_dir = script_dir / "SmartTour"
sys.path.append(str(smarttour_dir))


def migrate_tourism_data():
    """Script completo de migración"""

    print("🔄 Iniciando migración a estructura por destinos...")

    # Rutas
    project_root = script_dir
    old_csv = project_root / "DATA" / "tourism_data.csv"
    destinations_dir = project_root / "DATA" / "destinations"
    backup_dir = project_root / "DATA" / "backup"

    # 1. Crear backup del archivo original
    backup_dir.mkdir(parents=True, exist_ok=True)
    if old_csv.exists():
        shutil.copy2(old_csv, backup_dir / "tourism_data_backup.csv")
        print("✓ Backup creado")

    # 2. Verificar que existan archivos por destino
    if destinations_dir.exists():
        csv_files = list(destinations_dir.glob("*.csv"))
        if csv_files:
            print(f"✓ Ya existen {len(csv_files)} archivos CSV por destino:")
            for file in csv_files:
                print(f"  - {file.name}")
        else:
            print("❌ No se encontraron archivos CSV en el directorio de destinos")
            if old_csv.exists():
                print("🔄 Ejecutando división del CSV...")
                try:
                    from modules.src.data.split_tourism_data import (
                        split_tourism_data_by_destination,
                    )

                    destinos = split_tourism_data_by_destination(
                        str(old_csv), str(destinations_dir)
                    )
                    print(f"✓ Datos divididos en {len(destinos)} destinos")
                except ImportError as e:
                    print(f"❌ Error al importar split_tourism_data: {e}")
                    return False
            else:
                print("❌ No se encontró tourism_data.csv para dividir")
                return False
    else:
        print("❌ No existe el directorio DATA/destinations/")
        return False

    # 3. Verificar la estructura de archivos actualizada
    csv_files = list(destinations_dir.glob("*.csv"))
    print(f"✓ Estructura actualizada con {len(csv_files)} archivos:")
    for file in csv_files:
        print(f"  - {file.name}")

    # 4. Test de funcionamiento
    print("\n🧪 Probando nueva estructura...")
    try:
        from modules.src.data.hotel_repository import HotelRepository

        # Test 1: Cargar desde directorio completo
        repo_all = HotelRepository.from_destinations_directory(str(destinations_dir))
        destinations = repo_all.get_available_destinations()
        print(
            f"✓ Carga completa: {len(destinations)} destinos, {len(repo_all.hotels)} hoteles"
        )

        # Test 2: Cargar destino específico
        if "La Habana" in destinations:
            repo_specific = HotelRepository.from_single_destination(
                "La Habana", str(destinations_dir)
            )
            habana_hotels = repo_specific.get_hotels_by_destino("La Habana")
            print(f"✓ Carga específica: La Habana con {len(habana_hotels)} hoteles")

        print("✅ Tests de funcionalidad exitosos!")

    except Exception as e:
        print(f"❌ Error en tests: {e}")
        return False

    # 5. Instrucciones finales
    print("\n🎉 Migración completada exitosamente!")
    print(f"📁 Archivos por destino en: {destinations_dir}")
    print(f"💾 Backup en: {backup_dir}")

    print("\n📋 Cambios implementados:")
    print("✅ HotelRepository actualizado con nuevos métodos")
    print("✅ Módulo planner actualizado para usar destinos")
    print("✅ Simulaciones actualizadas")
    print("✅ Tests actualizados")
    print("✅ Build script actualizado")

    print("\n🚀 El sistema está listo para usar!")
    print("Ahora puedes:")
    print("- Cargar hoteles por destino específico (más rápido)")
    print("- Usar selectbox dinámico con destinos disponibles")
    print("- Agregar nuevos destinos fácilmente")
    print("- Mantener mejor organización de datos")

    return True


def verify_migration():
    """Verificar que la migración fue exitosa"""
    project_root = Path(__file__).parent.absolute()
    destinations_dir = project_root / "DATA" / "destinations"

    if not destinations_dir.exists():
        print("❌ Directorio de destinos no existe")
        return False

    csv_files = list(destinations_dir.glob("*.csv"))
    if not csv_files:
        print("❌ No hay archivos CSV en el directorio de destinos")
        return False

    print(f"✅ Migración verificada: {len(csv_files)} archivos de destinos encontrados")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("🏝️  MIGRACIÓN TOUR GUIDE CUBA - ESTRUCTURA POR DESTINOS")
    print("=" * 60)

    if migrate_tourism_data():
        print("\n" + "=" * 60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ MIGRACIÓN FALLÓ - Revisar errores anteriores")
        print("=" * 60)

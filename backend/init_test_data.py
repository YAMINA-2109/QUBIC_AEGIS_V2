"""
Script pour initialiser les données de test pour QUBIC AEGIS
"""
import asyncio
import sys
from app.services.test_data_generator import initialize_test_data

async def main():
    print("🔄 Initialisation des données de test...")
    try:
        await initialize_test_data(
            num_transactions=1000,
            force_regenerate=False
        )
        print("✅ Données de test initialisées avec succès!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())


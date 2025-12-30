#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Initialize database"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import db


def main():
    print("Initializing database...")
    print("=" * 60)
    
    try:
        print("\n1. Creating schema...")
        db.create_schema()
        
        print("\n2. Creating tables...")
        db.create_tables()
        
        print("\n3. Verifying...")
        stats = db.get_stats()
        
        print("\n" + "=" * 60)
        print("Database initialized successfully!")
        print("\nTables:")
        for table, count in stats.items():
            print(f"  - {table}: {count} rows")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

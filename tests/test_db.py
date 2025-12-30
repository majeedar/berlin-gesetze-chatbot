#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick database test"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import db
from src.database.models.models import Document


def main():
    print("Testing database...")
    
    stats = db.get_stats()
    print(f"Stats: {stats}")
    
    with db.session_scope() as session:
        doc = Document(
            title="Test Document",
            url="https://test.com/1",
            content="Test content",
            content_hash="hash123"
        )
        session.add(doc)
        session.flush()
        print(f"Created document ID: {doc.id}")
        session.delete(doc)
        print("Cleaned up test data")
    
    print("\nAll tests passed!")


if __name__ == "__main__":
    main()

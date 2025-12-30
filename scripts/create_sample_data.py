#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create sample Berlin law documents for testing"""
import sys
from pathlib import Path
import hashlib
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scraper.storage import DocumentStorage
from src.database.connection import db
from src.database.models.models import Document


def create_sample_documents():
    """Create sample documents for testing"""
    
    sample_docs = [
        {
            'title': 'Allgemeines Zuständigkeitsgesetz (AZG)',
            'content': '''# Allgemeines Zuständigkeitsgesetz

## Paragraph 1 Grundsatz
Die Zuständigkeit der Behörden richtet sich nach diesem Gesetz.

## Paragraph 2 Zuständige Behörden
(1) Zuständig ist die Behörde, in deren Bezirk der Anlass für die Amtshandlung hervortritt.
(2) Bei mehreren zuständigen Behörden entscheidet die übergeordnete Behörde.

## Paragraph 3 Delegation
Die Zuständigkeit kann auf nachgeordnete Behörden delegiert werden.''',
            'url': 'https://gesetze.berlin.de/bsbe/document/jlr-ZustGBErahmen',
            'doc_type': 'law'
        },
        {
            'title': 'Berliner Hochschulgesetz (BerlHG)',
            'content': '''# Berliner Hochschulgesetz

## Paragraph 1 Geltungsbereich
Dieses Gesetz gilt für alle Hochschulen des Landes Berlin.

## Paragraph 2 Aufgaben der Hochschulen
(1) Die Hochschulen dienen der Pflege und Entwicklung der Wissenschaften.
(2) Sie bereiten auf berufliche Tätigkeiten vor.

## Paragraph 3 Freiheit von Forschung und Lehre
Forschung und Lehre sind frei im Rahmen der Verfassung.''',
            'url': 'https://gesetze.berlin.de/bsbe/document/jlr-HSchulGBE',
            'doc_type': 'law'
        },
        {
            'title': 'Berliner Straßengesetz (BerlStrG)',
            'content': '''# Berliner Straßengesetz

## Paragraph 1 Straßen
(1) Straßen sind öffentliche Wege.
(2) Sie dienen dem öffentlichen Verkehr.

## Paragraph 2 Straßenbaulast
Die Straßenbaulast trägt das Land Berlin.

## Paragraph 3 Widmung
Straßen werden durch Widmung öffentlich.''',
            'url': 'https://gesetze.berlin.de/bsbe/document/jlr-StrGBErahmen',
            'doc_type': 'law'
        },
        {
            'title': 'Berliner Datenschutzgesetz (BlnDSG)',
            'content': '''# Berliner Datenschutzgesetz

## Paragraph 1 Zweck
Dieses Gesetz dient dem Schutz personenbezogener Daten.

## Paragraph 2 Anwendungsbereich
Es gilt für alle öffentlichen Stellen des Landes Berlin.

## Paragraph 3 Grundsätze
(1) Daten müssen rechtmäßig verarbeitet werden.
(2) Die Verarbeitung muss transparent sein.
(3) Daten müssen geschützt werden.''',
            'url': 'https://gesetze.berlin.de/bsbe/document/jlr-DSGBErahmen',
            'doc_type': 'law'
        },
        {
            'title': 'Berliner Bauordnung (BauO Bln)',
            'content': '''# Berliner Bauordnung

## Paragraph 1 Anwendungsbereich
Diese Verordnung gilt für das gesamte Gebiet des Landes Berlin.

## Paragraph 2 Genehmigungspflicht
(1) Bauliche Anlagen bedürfen der Genehmigung.
(2) Ausnahmen regelt die Bauordnung.

## Paragraph 3 Bauaufsichtsbehörde
Zuständig sind die Bezirksämter.''',
            'url': 'https://gesetze.berlin.de/bsbe/document/jlr-BauOBErahmen',
            'doc_type': 'ordinance'
        }
    ]
    
    # Add content hash and timestamp
    for doc in sample_docs:
        doc['content_hash'] = hashlib.sha256(doc['content'].encode()).hexdigest()
        doc['scraped_at'] = datetime.now().isoformat()
    
    return sample_docs


def main():
    print("="*60)
    print("Creating Sample Berlin Law Documents")
    print("="*60)
    
    documents = create_sample_documents()
    
    print(f"\nCreated {len(documents)} sample documents")
    
    storage = DocumentStorage()
    
    job_id = storage.create_scraping_job(
        job_type='sample_data',
        parameters={'count': len(documents)}
    )
    
    print(f"Created job ID: {job_id}")
    
    stats = storage.save_documents_batch(documents)
    
    print("\nSave statistics:")
    print(f"  Saved: {stats['saved']}")
    print(f"  Errors: {stats['errors']}")
    
    if job_id:
        storage.update_scraping_job(
            job_id=job_id,
            status='completed',
            stats={'documents_found': len(documents), 'saved': stats['saved']}
        )
    
    # Query documents properly with active session
    print("\nDocuments in database:")
    with db.session_scope() as session:
        docs = session.query(Document).order_by(Document.created_at.desc()).limit(10).all()
        for doc in docs:
            print(f"  [{doc.id}] {doc.title}")
    
    print(f"\nTotal: {storage.get_document_count()}")
    print("\n" + "="*60)
    print("Sample data created successfully!")
    print("="*60)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
preprocess.py

Unified script to run all preprocessing steps directly by importing modules,
including generating the source.txt file from a specified local path or remote URL:
1. Ingest source via gitingest.ingest (URL or local path)
2. Generate data/source.txt
3. Chunk data from data/source.txt into data/data_chunks.json
4. Generate context and produce data/final_data.json
5. Initialize the vector database (creates collection/table)
6. Populate the database with embeddings from final_data.json

Usage:
  python preprocess.py --source <LOCAL_PATH_OR_URL>
  python preprocess.py                  # uses existing data/source.txt in ./data
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
import json
import asyncio
import argparse
import tempfile
import shutil
import subprocess
from gitingest import ingest

# Import preprocessing modules
from src.preprocessing.chunk_splitter import (
    split_in_root_folders,
    aggregate_files_by_token,
    save_as_json,
)
from src.preprocessing.context_generator import generate_context

# Import database and embeddings modules
from src.core.database import build_search_db
from src.embeddings import populate_db


def generate_source(source_spec: str, data_dir: str = 'data') -> None:
    """Generate data/source.txt via gitingest.ingest or fallback to manual directory walk."""
    data_path = data_dir if os.path.isabs(data_dir) else os.path.join(os.getcwd(), data_dir)
    os.makedirs(data_path, exist_ok=True)
    dest = os.path.join(data_path, 'source.txt')

    # Try gitingest.ingest for URL or local path
    try:
        print(f"Running gitingest.ingest on {source_spec}...")
        summary, tree, content = ingest(source_spec)
        with open(dest, 'w', encoding='utf-8') as out:
            out.write("=== SUMMARY ===\n")
            out.write(str(summary) + "\n\n")
            out.write("=== TREE ===\n")
            out.write(str(tree) + "\n\n")
            out.write("=== CONTENT ===\n")
            out.write(str(content) + "\n")
        print("Generated source.txt via gitingest.ingest().")
        return
    except Exception as e:
        print(f"gitingest.ingest() failed ({e}), falling back to manual walk...")

    # Manual fallback: local directory walk
    if not os.path.isdir(source_spec):
        sys.exit(f"Error: manual fallback requires a local directory, got: {source_spec}")

    print(f"Generating source.txt via manual walk from {source_spec}...")
    with open(dest, 'w', encoding='utf-8') as out:
        for root, dirs, files in os.walk(source_spec):
            dirs[:] = [d for d in dirs if d not in ['.git', os.path.basename(data_path)]]
            for fname in files:
                path = os.path.join(root, fname)
                rel = os.path.relpath(path, source_spec)
                out.write(f"===== {rel} =====\n")
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        out.write(f.read())
                except Exception as ex:
                    out.write(f"[Error reading file: {ex}]\n")
                out.write("\n")
    print("Generated source.txt via manual directory walk.")


def chunk_data(data_dir: str):
    """Chunk the source.txt into data_chunks.json."""
    src = os.path.join(data_dir, 'source.txt')
    out_file = 'data_chunks.json'
    print(f"Chunking data from {src}...")
    split_data = split_in_root_folders(src)
    grouped = aggregate_files_by_token(split_data)
    save_as_json(grouped, data_dir, file_name=out_file)
    print(f"Saved chunks to {os.path.join(data_dir, out_file)}")


def generate_context_data(data_dir: str):
    """Enrich chunks with context to produce final_data.json."""
    chunk_file = os.path.join(data_dir, 'data_chunks.json')
    print(f"Loading chunked data from {chunk_file}...")
    with open(chunk_file, 'r', encoding='utf-8') as f:
        data_chunks = json.load(f)
    print("Generating context for each chunk...")
    contextual = asyncio.run(generate_context(data_chunks))
    merged = {key: [f"{ctx}\n{chunk}" for ctx, chunk in zip(contextual[key], data_chunks[key])] for key in data_chunks}
    save_as_json(data=merged, output_dir=data_dir, file_name='final_data.json')
    print(f"Saved final data to {os.path.join(data_dir, 'final_data.json')}")


def setup_database():
    """Initialize the vector database (creates table and extension if not exists)."""
    print("Initializing vector database...")
    asyncio.run(build_search_db())
    print("Database initialized.")


def generate_embeddings(data_dir: str):
    """Populate the database with embeddings from final_data.json."""
    final_file = os.path.join(data_dir, 'final_data.json')
    print(f"Loading final data from {final_file}...")
    with open(final_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("Generating and inserting embeddings...")
    asyncio.run(populate_db(data))
    print("Embeddings populated.")


def main():
    parser = argparse.ArgumentParser(description='Preprocess pipeline with source ingestion')
    parser.add_argument('--source', help='Local path or remote URL for ingestion')
    parser.add_argument('--data-dir', default='data', help='Data directory name')
    args = parser.parse_args()

    project_root = os.getcwd()
    data_dir = "data"

    # Determine source specification
    source_spec = args.source or project_root

    source_path = os.path.join(data_dir, 'source.txt')
    if args.source:
        generate_source(source_spec, data_dir)
    else:
        if not os.path.exists(source_path):
            sys.exit(f"Error: source.txt not found at {source_path}. Please provide --source to generate it.")
        print(f"Using existing source.txt at {source_path}, skipping generation.")

    # Run processing steps
    chunk_data(data_dir)
    generate_context_data(data_dir)
    setup_database()
    generate_embeddings(data_dir)


if __name__ == '__main__':
    main()

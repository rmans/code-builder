#!/usr/bin/env python3
"""
Master File Synchronization

This module provides comprehensive master file synchronization for all document types.
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ..config.settings import get_config


class MasterFileSync:
    """Handles synchronization of master files for all document types."""
    
    def __init__(self, docs_dir: str = None):
        config = get_config()
        if docs_dir is None:
            docs_dir = config.get_effective_docs_dir()
        
        self.docs_dir = Path(docs_dir)
        self.master_files = {
            "prd": self.docs_dir / "prd" / "0000_MASTER_PRD.md",
            "adr": self.docs_dir / "adrs" / "0000_MASTER_ADR.md",
            "arch": self.docs_dir / "arch" / "0000_MASTER_ARCH.md",
            "int": self.docs_dir / "exec" / "0000_MASTER_INT.md",
            "impl": self.docs_dir / "impl" / "0000_MASTER_IMPL.md",
            "exec": self.docs_dir / "exec" / "0000_MASTER_EXEC.md",
            "task": self.docs_dir / "tasks" / "0000_MASTER_TASK.md",
            "ux": self.docs_dir / "ux" / "0000_MASTER_UX.md"
        }
    
    def sync_all_master_files(self) -> Dict[str, Any]:
        """Synchronize all master files."""
        results = {}
        
        for doc_type, master_file in self.master_files.items():
            try:
                result = self.sync_master_file(doc_type)
                results[doc_type] = result
            except Exception as e:
                results[doc_type] = {"status": "error", "error": str(e)}
        
        return results
    
    def sync_master_file(self, doc_type: str) -> Dict[str, Any]:
        """Synchronize a specific master file."""
        master_file = self.master_files.get(doc_type)
        if not master_file or not master_file.exists():
            return {"status": "skipped", "reason": "Master file not found"}
        
        try:
            # Read master file
            with open(master_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.startswith('---'):
                return {"status": "skipped", "reason": "No frontmatter found"}
            
            # Parse frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {"status": "skipped", "reason": "Invalid frontmatter format"}
            
            frontmatter_text = parts[1]
            body = parts[2]
            
            try:
                frontmatter = yaml.safe_load(frontmatter_text) or {}
            except yaml.YAMLError as e:
                return {"status": "error", "error": f"YAML parse error: {e}"}
            
            # Get documents from frontmatter
            documents = frontmatter.get('documents', [])
            
            # Remove documents from frontmatter (it should only be in the table)
            if 'documents' in frontmatter:
                del frontmatter['documents']
            
            # Generate table
            table_lines = self._generate_table(doc_type, documents, frontmatter)
            
            # Reconstruct content
            new_body = '\n'.join(table_lines)
            new_content = '---\n' + yaml.dump(frontmatter, sort_keys=False).strip() + '\n---\n\n' + new_body
            
            # Write back to file
            with open(master_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return {
                "status": "success",
                "documents_count": len(documents),
                "file": str(master_file)
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _generate_table(self, doc_type: str, documents: List[Dict[str, Any]], frontmatter: Dict[str, Any]) -> List[str]:
        """Generate table content for master file."""
        if not documents:
            return [
                f"# {frontmatter.get('title', 'Index')}",
                "",
                "| ID | Title | Status | Domain | Link |",
                "|---|---|---|---|---|",
                "| *No documents currently defined* |  |  |  |  |"
            ]
        
        # Sort documents by ID for consistent ordering
        sorted_docs = sorted(documents, key=lambda x: x.get('id', ''))
        
        table_lines = [
            f"# {frontmatter.get('title', 'Index')}",
            "",
            "| ID | Title | Status | Domain | Link |",
            "|---|---|---|---|---|"
        ]
        
        for doc in sorted_docs:
            doc_id = doc.get('id', '')
            title = doc.get('title', '')
            status = doc.get('status', '')
            domain = doc.get('domain', '')
            link = f"[{doc_id}]({doc_id}.md)" if doc_id else ""
            
            table_lines.append(f"| {doc_id} | {title} | {status} | {domain} | {link} |")
        
        return table_lines
    
    def add_document_to_master(self, doc_type: str, doc_info: Dict[str, Any]) -> bool:
        """Add a document to its master file."""
        master_file = self.master_files.get(doc_type)
        if not master_file or not master_file.exists():
            return False
        
        try:
            # Read master file
            with open(master_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.startswith('---'):
                return False
            
            # Parse frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                return False
            
            frontmatter_text = parts[1]
            body = parts[2]
            
            try:
                frontmatter = yaml.safe_load(frontmatter_text) or {}
            except yaml.YAMLError:
                return False
            
            # Get documents from frontmatter
            documents = frontmatter.get('documents', [])
            
            # Check if document already exists
            doc_id = doc_info.get('id', '')
            existing_doc = next((d for d in documents if d.get('id') == doc_id), None)
            
            if existing_doc:
                # Update existing document
                existing_doc.update(doc_info)
            else:
                # Add new document
                documents.append(doc_info)
            
            # Update frontmatter
            frontmatter['documents'] = documents
            
            # Generate table
            table_lines = self._generate_table(doc_type, documents, frontmatter)
            
            # Reconstruct content
            new_body = '\n'.join(table_lines)
            new_content = '---\n' + yaml.dump(frontmatter, sort_keys=False).strip() + '\n---\n\n' + new_body
            
            # Write back to file
            with open(master_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            print(f"Error adding document to master file: {e}")
            return False
    
    def remove_document_from_master(self, doc_type: str, doc_id: str) -> bool:
        """Remove a document from its master file."""
        master_file = self.master_files.get(doc_type)
        if not master_file or not master_file.exists():
            return False
        
        try:
            # Read master file
            with open(master_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.startswith('---'):
                return False
            
            # Parse frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                return False
            
            frontmatter_text = parts[1]
            body = parts[2]
            
            try:
                frontmatter = yaml.safe_load(frontmatter_text) or {}
            except yaml.YAMLError:
                return False
            
            # Get documents from frontmatter
            documents = frontmatter.get('documents', [])
            
            # Remove document
            documents = [d for d in documents if d.get('id') != doc_id]
            
            # Update frontmatter
            frontmatter['documents'] = documents
            
            # Generate table
            table_lines = self._generate_table(doc_type, documents, frontmatter)
            
            # Reconstruct content
            new_body = '\n'.join(table_lines)
            new_content = '---\n' + yaml.dump(frontmatter, sort_keys=False).strip() + '\n---\n\n' + new_body
            
            # Write back to file
            with open(master_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            print(f"Error removing document from master file: {e}")
            return False
    
    def validate_master_files(self) -> Dict[str, Any]:
        """Validate all master files for consistency."""
        results = {}
        
        for doc_type, master_file in self.master_files.items():
            try:
                if not master_file.exists():
                    results[doc_type] = {"status": "missing", "file": str(master_file)}
                    continue
                
                # Read and parse master file
                with open(master_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if not content.startswith('---'):
                    results[doc_type] = {"status": "invalid", "reason": "No frontmatter"}
                    continue
                
                parts = content.split('---', 2)
                if len(parts) < 3:
                    results[doc_type] = {"status": "invalid", "reason": "Invalid frontmatter format"}
                    continue
                
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError as e:
                    results[doc_type] = {"status": "invalid", "reason": f"YAML error: {e}"}
                    continue
                
                documents = frontmatter.get('documents', [])
                
                # Check for duplicate IDs
                doc_ids = [d.get('id') for d in documents if d.get('id')]
                duplicate_ids = [id for id in set(doc_ids) if doc_ids.count(id) > 1]
                
                # Check for missing files
                missing_files = []
                for doc in documents:
                    doc_id = doc.get('id')
                    if doc_id:
                        doc_file = master_file.parent / f"{doc_id}.md"
                        if not doc_file.exists():
                            missing_files.append(doc_id)
                
                results[doc_type] = {
                    "status": "valid",
                    "documents_count": len(documents),
                    "duplicate_ids": duplicate_ids,
                    "missing_files": missing_files,
                    "file": str(master_file)
                }
                
            except Exception as e:
                results[doc_type] = {"status": "error", "error": str(e)}
        
        return results


def create_master_sync(docs_dir: str = None) -> MasterFileSync:
    """Create a new MasterFileSync instance."""
    return MasterFileSync(docs_dir)


# Global sync instance
master_sync = create_master_sync()


def sync_all_master_files() -> Dict[str, Any]:
    """Sync all master files using the global instance."""
    return master_sync.sync_all_master_files()


def sync_master_file(doc_type: str) -> Dict[str, Any]:
    """Sync a specific master file using the global instance."""
    return master_sync.sync_master_file(doc_type)


def add_document_to_master(doc_type: str, doc_info: Dict[str, Any]) -> bool:
    """Add a document to its master file using the global instance."""
    return master_sync.add_document_to_master(doc_type, doc_info)


def validate_master_files() -> Dict[str, Any]:
    """Validate all master files using the global instance."""
    return master_sync.validate_master_files()

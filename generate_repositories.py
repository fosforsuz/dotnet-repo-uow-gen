#!/usr/bin/env python3
"""
Repogen: Clean Architecture .NET Repository & UnitOfWork Generator
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional, Tuple

from templates.templates import (
    TEMPLATE_INTERFACE,
    TEMPLATE_IMPLEMENTATION,
    TEMPLATE_UOW_INTERFACE_HEADER,
    TEMPLATE_UOW_INTERFACE_FOOTER,
    TEMPLATE_UOW_IMPL_HEADER,
    TEMPLATE_UOW_IMPL_REPO_PROPERTY,
    TEMPLATE_UOW_IMPL_FOOTER,
    TEMPLATE_REPOSITORY_INTERFACE_WITH_COMMENTS,
    TEMPLATE_REPOSITORY_IMPLEMENTATION
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# -------------------------------
# Utility Functions
# -------------------------------

def get_entity_names(entity_path: Path) -> List[str]:
    if not entity_path.exists():
        logger.error(f"Entity directory not found: {entity_path}")
        return []
    return [f.stem for f in entity_path.glob("*.cs")]

def detect_context_class(context_path: Path) -> str:
    if not context_path.exists():
        logger.warning(f"Context directory not found: {context_path}")
        return "AppDbContext"
    for file in context_path.glob("*.cs"):
        return file.stem
    return "AppDbContext"

def create_directory(path: Path, dry_run: bool = False) -> None:
    if dry_run:
        logger.info(f"[DRY RUN] Would create directory: {path}")
        return
    path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Directory ensured: {path}")

def write_file_safe(path: Path, content: str, dry_run: bool = False) -> None:
    if dry_run:
        logger.info(f"[DRY RUN] Would create: {path}")
    elif not path.exists():
        try:
            path.write_text(content)
            logger.info(f"Created: {path}")
        except Exception as e:
            logger.error(f"Error writing file {path}: {e}")
            raise

def validate_project_structure(base_path: Path) -> Tuple[bool, Optional[str]]:
    namespace = base_path.name
    required_dirs = [
        base_path / f"{namespace}.Domain" / "Entity",
        base_path / f"{namespace}.Infrastructure" / "Context"
    ]
    for dir_path in required_dirs:
        if not dir_path.exists():
            return False, f"Missing required directory: {dir_path}"
    return True, None


# -------------------------------
# Core Generation Logic
# -------------------------------

def generate_repositories(namespace: str, abstractions_path: Path, repos_path: Path, entity_names: List[str],
                          context_class: str, dry_run: bool):
    for entity in entity_names:
        interface_path = abstractions_path / f"I{entity}Repository.cs"
        impl_path = repos_path / f"{entity}Repository.cs"

        interface_code = TEMPLATE_INTERFACE.format(namespace=namespace, name=entity)
        impl_code = TEMPLATE_IMPLEMENTATION.format(namespace=namespace, name=entity, context_class=context_class)

        write_file_safe(interface_path, interface_code, dry_run)
        write_file_safe(impl_path, impl_code, dry_run)


def generate_unit_of_work(namespace: str, base_dir: Path, entity_names: List[str],
                          context_class: str, dry_run: bool):
    interface_props = ""
    impl_props = ""

    for entity in entity_names:
        repo_interface = f"I{entity}Repository"
        prop_name = f"{entity}Repository"
        interface_props += f"    {repo_interface} {prop_name} {{ get; }}\n"
        impl_props += TEMPLATE_UOW_IMPL_REPO_PROPERTY.format(interface_name=repo_interface, property_name=prop_name)

    uow_interface_code = (
        TEMPLATE_UOW_INTERFACE_HEADER.format(namespace=namespace)
        + interface_props
        + TEMPLATE_UOW_INTERFACE_FOOTER
    )
    uow_impl_code = (
        TEMPLATE_UOW_IMPL_HEADER.format(namespace=namespace, context_class=context_class)
        + impl_props
        + TEMPLATE_UOW_IMPL_FOOTER
    )

    write_file_safe(base_dir / "IUnitOfWork.cs", uow_interface_code, dry_run)
    write_file_safe(base_dir / "UnitOfWork.cs", uow_impl_code, dry_run)


def generate_generic_repository(namespace: str, base_dir: Path, dry_run: bool):
    repo_interface_code = TEMPLATE_REPOSITORY_INTERFACE_WITH_COMMENTS.format(namespace=namespace)
    repo_impl_code = TEMPLATE_REPOSITORY_IMPLEMENTATION.format(namespace=namespace)

    write_file_safe(base_dir / "IRepository.cs", repo_interface_code, dry_run)
    write_file_safe(base_dir / "Repository.cs", repo_impl_code, dry_run)


# -------------------------------
# Entry Point
# -------------------------------

def generate_all(base_path: Path, dry_run: bool = False) -> None:
    namespace = base_path.name
    valid, err = validate_project_structure(base_path)
    if not valid:
        raise RuntimeError(err)

    entity_path = base_path / f"{namespace}.Domain" / "Entity"
    context_path = base_path / f"{namespace}.Infrastructure" / "Context"
    abstractions_path = base_path / f"{namespace}.Infrastructure" / "Abstractions"
    repos_path = base_path / f"{namespace}.Infrastructure" / "Repositories"
    base_dir = base_path / f"{namespace}.Infrastructure" / "Base"

    for path in [abstractions_path, repos_path, base_dir]:
        create_directory(path, dry_run)

    entity_names = get_entity_names(entity_path)
    if not entity_names:
        logger.warning("No entity files found.")
        return

    context_class = detect_context_class(context_path)

    generate_repositories(namespace, abstractions_path, repos_path, entity_names, context_class, dry_run)
    generate_unit_of_work(namespace, base_dir, entity_names, context_class, dry_run)
    generate_generic_repository(namespace, base_dir, dry_run)

    logger.info("✅ Repository, UnitOfWork, and GenericRepository generation completed.")


def main():
    parser = argparse.ArgumentParser(description="Generate .NET Repository and UnitOfWork classes")
    parser.add_argument("--path", required=True, help="Project root path")
    parser.add_argument("--dry-run", action="store_true", help="Preview file creation without writing")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    base_path = Path(args.path).resolve()
    if not base_path.exists() or not base_path.is_dir():
        logger.error(f"Invalid path: {base_path}")
        sys.exit(1)

    try:
        generate_all(base_path, dry_run=args.dry_run)
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

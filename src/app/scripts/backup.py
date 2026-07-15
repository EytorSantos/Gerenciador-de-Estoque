#!/usr/bin/env python3
"""
Script de Backup Automático para o Sistema de Gestão de Estoque.

Implementa RNF04: Criar rotina automática de backup.

Uso:
    python backup.py  # Faz backup imediato
    python backup.py --schedule  # Agenda backups periódicos
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import argparse
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class BackupManager:
    """Gerencia backups do banco de dados PostgreSQL."""
    
    def __init__(self, backup_dir: str = "backups"):
        """
        Inicializa o gerenciador de backup.
        
        Args:
            backup_dir: Diretório onde os backups serão armazenados.
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Carregar variáveis de ambiente
        self.db_host = os.getenv("DATABASE_HOST", "db")
        self.db_port = os.getenv("DATABASE_PORT", "5432")
        self.db_name = os.getenv("DATABASE_NAME", "pharmacy_stock")
        self.db_user = os.getenv("DATABASE_USER", "postgres")
        self.db_password = os.getenv("DATABASE_PASSWORD", "postgres")
    
    def create_backup(self) -> bool:
        """
        Cria um backup do banco de dados.
        
        Returns:
            True se o backup foi bem-sucedido, False caso contrário.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"pharmacy_stock_{timestamp}.sql"
        
        try:
            logger.info(f"Iniciando backup para {backup_file}...")
            
            # Comando pg_dump
            cmd = [
                "pg_dump",
                "-h", self.db_host,
                "-p", self.db_port,
                "-U", self.db_user,
                "-d", self.db_name,
                "-F", "c",  # Formato comprimido
                "-f", str(backup_file)
            ]
            
            # Definir senha via variável de ambiente
            env = os.environ.copy()
            env["PGPASSWORD"] = self.db_password
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✓ Backup criado com sucesso: {backup_file}")
                logger.info(f"  Tamanho: {backup_file.stat().st_size / 1024 / 1024:.2f} MB")
                return True
            else:
                logger.error(f"✗ Erro ao criar backup: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"✗ Exceção ao criar backup: {str(e)}")
            return False
    
    def restore_backup(self, backup_file: str) -> bool:
        """
        Restaura um backup do banco de dados.
        
        Args:
            backup_file: Caminho do arquivo de backup.
        
        Returns:
            True se a restauração foi bem-sucedida, False caso contrário.
        """
        try:
            logger.info(f"Iniciando restauração de {backup_file}...")
            
            # Comando pg_restore
            cmd = [
                "pg_restore",
                "-h", self.db_host,
                "-p", self.db_port,
                "-U", self.db_user,
                "-d", self.db_name,
                "-c",  # Limpar banco antes de restaurar
                str(backup_file)
            ]
            
            # Definir senha via variável de ambiente
            env = os.environ.copy()
            env["PGPASSWORD"] = self.db_password
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✓ Backup restaurado com sucesso")
                return True
            else:
                logger.error(f"✗ Erro ao restaurar backup: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"✗ Exceção ao restaurar backup: {str(e)}")
            return False
    
    def list_backups(self) -> list:
        """
        Lista todos os backups disponíveis.
        
        Returns:
            Lista de arquivos de backup.
        """
        backups = sorted(self.backup_dir.glob("pharmacy_stock_*.sql"))
        return backups
    
    def cleanup_old_backups(self, keep_count: int = 10) -> None:
        """
        Remove backups antigos, mantendo apenas os mais recentes.
        
        Args:
            keep_count: Número de backups mais recentes a manter.
        """
        backups = self.list_backups()
        
        if len(backups) > keep_count:
            to_delete = backups[:-keep_count]
            for backup in to_delete:
                try:
                    backup.unlink()
                    logger.info(f"✓ Backup antigo removido: {backup.name}")
                except Exception as e:
                    logger.error(f"✗ Erro ao remover {backup.name}: {str(e)}")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Sistema de Backup para Farmácia Stock"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Criar um backup imediato"
    )
    parser.add_argument(
        "--restore",
        type=str,
        help="Restaurar um backup específico"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar backups disponíveis"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remover backups antigos"
    )
    parser.add_argument(
        "--backup-dir",
        type=str,
        default="backups",
        help="Diretório de backups (padrão: backups)"
    )
    
    args = parser.parse_args()
    
    manager = BackupManager(backup_dir=args.backup_dir)
    
    if args.backup or (not args.restore and not args.list and not args.cleanup):
        # Padrão: criar backup
        success = manager.create_backup()
        if success:
            manager.cleanup_old_backups(keep_count=10)
        sys.exit(0 if success else 1)
    
    if args.restore:
        success = manager.restore_backup(args.restore)
        sys.exit(0 if success else 1)
    
    if args.list:
        backups = manager.list_backups()
        if backups:
            logger.info("Backups disponíveis:")
            for backup in backups:
                size_mb = backup.stat().st_size / 1024 / 1024
                logger.info(f"  - {backup.name} ({size_mb:.2f} MB)")
        else:
            logger.info("Nenhum backup encontrado.")
        sys.exit(0)
    
    if args.cleanup:
        manager.cleanup_old_backups(keep_count=10)
        sys.exit(0)


if __name__ == "__main__":
    main()

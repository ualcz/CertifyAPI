import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CleanupService:
    """
    Serviço para limpeza automática de arquivos temporários gerados.
    """
    
    @staticmethod
    def cleanup_old_files(directory: str = "generated_certificates", max_age_hours: int = 24) -> dict:
        """
        Remove arquivos PDF e ZIP mais antigos que o tempo especificado.
        
        Args:
            directory: Diretório contendo os arquivos a serem limpos
            max_age_hours: Idade máxima dos arquivos em horas (padrão: 24h)
            
        Returns:
            Dict com estatísticas da limpeza
        """
        if not os.path.exists(directory):
            logger.warning(f"Diretório {directory} não existe. Nada a limpar.")
            return {
                "status": "skipped",
                "reason": "directory_not_found",
                "deleted_files": 0,
                "freed_space_mb": 0
            }
        
        cutoff_time = time.time() - (max_age_hours * 3600)
        deleted_count = 0
        freed_space = 0
        errors = []
        
        try:
            for filename in os.listdir(directory):
                # Processar apenas PDFs e ZIPs
                if not (filename.endswith('.pdf') or filename.endswith('.zip')):
                    continue
                
                filepath = os.path.join(directory, filename)
                
                try:
                    file_stat = os.stat(filepath)
                    file_age = file_stat.st_mtime
                    
                    # Se o arquivo é mais antigo que o limite
                    if file_age < cutoff_time:
                        file_size = file_stat.st_size
                        os.remove(filepath)
                        deleted_count += 1
                        freed_space += file_size
                        logger.info(f"Arquivo removido: {filename} ({file_size / 1024:.2f} KB)")
                
                except Exception as e:
                    error_msg = f"Erro ao processar {filename}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
        
        except Exception as e:
            logger.error(f"Erro ao listar diretório {directory}: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "deleted_files": deleted_count,
                "freed_space_mb": round(freed_space / (1024 * 1024), 2)
            }
        
        logger.info(f"Limpeza concluída: {deleted_count} arquivos removidos, "
                   f"{freed_space / (1024 * 1024):.2f} MB liberados")
        
        return {
            "status": "success",
            "deleted_files": deleted_count,
            "freed_space_mb": round(freed_space / (1024 * 1024), 2),
            "max_age_hours": max_age_hours,
            "errors": errors if errors else None
        }
    
    @staticmethod
    def get_directory_stats(directory: str = "generated_certificates") -> dict:
        """
        Retorna estatísticas sobre o diretório de arquivos gerados.
        
        Returns:
            Dict com estatísticas do diretório
        """
        if not os.path.exists(directory):
            return {
                "exists": False,
                "total_files": 0,
                "total_size_mb": 0,
                "pdf_count": 0,
                "zip_count": 0
            }
        
        total_files = 0
        total_size = 0
        pdf_count = 0
        zip_count = 0
        oldest_file_age_hours = None
        
        try:
            current_time = time.time()
            
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                
                if os.path.isfile(filepath):
                    total_files += 1
                    file_stat = os.stat(filepath)
                    total_size += file_stat.st_size
                    
                    # Calcular idade do arquivo mais antigo
                    file_age_hours = (current_time - file_stat.st_mtime) / 3600
                    if oldest_file_age_hours is None or file_age_hours > oldest_file_age_hours:
                        oldest_file_age_hours = file_age_hours
                    
                    if filename.endswith('.pdf'):
                        pdf_count += 1
                    elif filename.endswith('.zip'):
                        zip_count += 1
        
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {"error": str(e)}
        
        return {
            "exists": True,
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "pdf_count": pdf_count,
            "zip_count": zip_count,
            "oldest_file_age_hours": round(oldest_file_age_hours, 2) if oldest_file_age_hours else 0
        }

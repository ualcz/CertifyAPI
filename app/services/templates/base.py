from abc import ABC, abstractmethod
from typing import Any, Dict
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4

class CertificateTemplate(ABC):
    """
    Classe base abstrata para templates de certificados.
    Novos templates devem herdar desta classe.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome único do template para registro"""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Descrição legível do template"""
        pass

    def generate(self, data: Dict[str, Any], output_path: str) -> str:
        """
        Gera o arquivo PDF do certificado.
        
        A implementação padrão usa o ReportLab e chama o método 'draw'.
        Templates baseados em HTML devem sobrescrever este método.
        """
        c = canvas.Canvas(output_path, pagesize=landscape(A4))
        self.draw(c, data)
        c.save()
        return output_path

    def draw(self, canvas: Any, data: Dict[str, Any]) -> None:
        """
        Desenha o certificado no canvas (apenas para templates ReportLab).
        
        Args:
            canvas: Objeto canvas do ReportLab
            data: Dicionário contendo os dados do certificado
        """
        raise NotImplementedError("Templates que não sobrescrevem 'generate' devem implementar 'draw'")

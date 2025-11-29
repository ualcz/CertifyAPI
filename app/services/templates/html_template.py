import os
from typing import Any, Dict
from jinja2 import Template
from xhtml2pdf import pisa
from .base import CertificateTemplate

class HtmlTemplate(CertificateTemplate):
    def __init__(self, name: str, file_path: str):
        self._name = name
        self._file_path = file_path
        
    @property
    def name(self) -> str:
        return self._name
        
    @property
    def description(self) -> str:
        return f"Template HTML: {self._name}"

    def generate(self, data: Dict[str, Any], output_path: str) -> str:
  
        with open(self._file_path, 'r', encoding='utf-8') as f:
            template_content = f.read()  
    
        template_data = data.copy()
        if 'issue_date' in template_data and hasattr(template_data['issue_date'], 'strftime'):
            template_data['issue_date'] = template_data['issue_date'].strftime("%d/%m/%Y")
            
        template = Template(template_content)
        rendered_html = template.render(**template_data)
        
        with open(output_path, "wb") as output_file:
            pisa_status = pisa.CreatePDF(
                src=rendered_html,
                dest=output_file,
                encoding='utf-8'
            )
            
        if pisa_status.err:
            raise Exception(f"Erro ao gerar PDF: {pisa_status.err}")
        
        return output_path

import os
from typing import Dict, Type, List, Union
from .base import CertificateTemplate
from .html_template import HtmlTemplate

class TemplateRegistry:
    _templates: Dict[str, Union[Type[CertificateTemplate], CertificateTemplate]] = {}
    
    @classmethod
    def register(cls, template_cls: Type[CertificateTemplate]):
        """Registra uma nova classe de template"""
        instance = template_cls()
        cls._templates[instance.name] = template_cls
        return template_cls
        
    @classmethod
    def register_instance(cls, template_instance: CertificateTemplate):
        """Registra uma instância de template (usado para HTML templates)"""
        cls._templates[template_instance.name] = template_instance
    
    @classmethod
    def get_template(cls, name: str) -> CertificateTemplate:
        """Retorna uma instância do template pelo nome"""
        if name not in cls._templates:
            cls.discover_html_templates()
            
        template_or_cls = cls._templates.get(name)
        
        if not template_or_cls:
            template_or_cls = cls._templates.get('default')
            if not template_or_cls:
                raise ValueError(f"Template '{name}' not found and no default available")
        
        if isinstance(template_or_cls, type):
            return template_or_cls()
        if isinstance(template_or_cls, type):
            return template_or_cls()
        return template_or_cls
    
    @classmethod
    def list_templates(cls) -> List[Dict[str, str]]:
        """Lista todos os templates registrados"""
        cls.discover_html_templates()
        
        result = []
        for name, item in cls._templates.items():
            instance = item() if isinstance(item, type) else item
            result.append({
                "id": name, 
                "name": instance.name,
                "description": instance.description
            })
        return result

    @classmethod
    def discover_html_templates(cls):
        """Procura por arquivos .html na pasta de templates e os registra"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(current_dir, "..", "..", "templates", "certificates")
        templates_dir = os.path.abspath(templates_dir)
        
        if not os.path.exists(templates_dir):
            return
            
        for filename in os.listdir(templates_dir):
            if filename.endswith(".html"):
                name = os.path.splitext(filename)[0]
                if name in cls._templates:
                    continue
                    
                file_path = os.path.join(templates_dir, filename)
                template = HtmlTemplate(name, file_path)
                cls.register_instance(template)


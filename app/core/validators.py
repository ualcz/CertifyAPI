"""
Validadores reutilizáveis para schemas Pydantic.
"""


def validate_cpf(cpf: str) -> str:
    """
    Valida formato de CPF brasileiro.
    
    Args:
        cpf: String contendo apenas dígitos do CPF
        
    Returns:
        CPF validado
        
    Raises:
        ValueError: Se o CPF não tiver 11 dígitos numéricos
    """
    if not cpf:
        raise ValueError('CPF é obrigatório')
    
    if len(cpf) != 11 or not cpf.isdigit():
        raise ValueError('CPF deve conter exatamente 11 dígitos numéricos')
    
    return cpf

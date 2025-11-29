import os
import zipfile
from typing import List, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.certificate import Certificate
from app.models.student import Student
from app.models.course import Course
from app.services.templates.registry import TemplateRegistry

def generate_certificate_pdf(certificate: Certificate, student: Optional[Student] = None, course: Optional[Course] = None) -> str:
    """
    Gera um arquivo PDF para o certificado usando o sistema de templates.
    Prioriza dados do snapshot (histórico) se disponíveis.
    """

    output_dir = "generated_certificates"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filename = f"{output_dir}/{certificate.uuid}.pdf"
    
    data = {}
    
  
    if certificate.data_snapshot:
        data = certificate.data_snapshot
        data['issue_date'] = certificate.issue_date
        data['uuid'] = certificate.uuid
    else:
        if not student or not course:
            raise ValueError("Student and Course must be provided if no snapshot exists")
            
        data = {
            'student_name': student.name,
            'student_cpf': student.cpf,
            'course_name': course.name,
            'course_workload': course.workload,
            'issue_date': certificate.issue_date,
            'uuid': certificate.uuid
        }
    
    if isinstance(data.get('issue_date'), str):
        try:
            data['issue_date'] = datetime.fromisoformat(data['issue_date'])
        except:
            pass 
            
    template_name = certificate.template_id or "default"
    template = TemplateRegistry.get_template(template_name)
    
    template.generate(data, filename)
    
    return filename

def generate_bulk_certificates_zip(certificates: List[Certificate], db: Session, class_id: int) -> str:
    """
    Gera múltiplos certificados em PDF e os empacota em um arquivo ZIP.
    Os PDFs individuais são removidos automaticamente após serem adicionados ao ZIP.
    """
    output_dir = "generated_certificates"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"{output_dir}/certificados_turma_{class_id}_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for certificate in certificates:
            student = None
            course = None
            
            if not certificate.data_snapshot:
                student = db.query(Student).filter(Student.id == certificate.student_id).first()
                course = db.query(Course).filter(Course.id == certificate.course_id).first()
                if not student or not course:
                    continue
            
            try:
                pdf_path = generate_certificate_pdf(certificate, student, course)
                
                student_name = certificate.data_snapshot.get('student_name') if certificate.data_snapshot else student.name
                
                safe_name = "".join(c for c in student_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_name = safe_name.replace(' ', '_')
                pdf_name_in_zip = f"certificado_{safe_name}_{certificate.uuid}.pdf"
                
                # Adicionar PDF ao ZIP
                zipf.write(pdf_path, arcname=pdf_name_in_zip)
                
                # Remover o PDF individual após adicioná-lo ao ZIP
                try:
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
                        print(f"✓ PDF individual removido: {pdf_path}")
                except Exception as e:
                    print(f"⚠ Erro ao remover PDF {pdf_path}: {e}")
                
            except Exception as e:
                print(f"Error generating certificate {certificate.uuid}: {e}")
                continue
    
    return zip_filename


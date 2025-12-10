import os
import tempfile

# Fix for ReportLab/xhtml2pdf temp dir issue
# Force use of local temp directory to avoid permission issues with system temp
temp_dir = os.path.abspath("data/temp")
os.makedirs(temp_dir, exist_ok=True)
os.environ['TEMP'] = temp_dir
os.environ['TMP'] = temp_dir
tempfile.tempdir = temp_dir

import markdown
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, Preformatted
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
import os

def generate_pdf_from_markdown(markdown_text: str, output_path: str) -> bool:
    """
    Markdown 텍스트를 PDF 파일로 변환하여 저장합니다.
    ReportLab을 직접 사용하여 폰트 및 스타일을 제어합니다.
    """
    try:
        # 1. 폰트 등록
        font_path = os.path.abspath("data/fonts/NanumGothic.ttf")
        font_name = "NanumGothic"
        
        if not os.path.exists(font_path):
            # 폰트 파일이 없으면 시스템 폰트 시도
            font_path = "C:/Windows/Fonts/malgun.ttf"
            font_name = "MalgunGothic"
            
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
            except Exception as e:
                print(f"폰트 등록 실패: {e}")
                font_name = "Helvetica" # Fallback
        else:
            font_name = "Helvetica"

        # 2. 스타일 정의
        styles = getSampleStyleSheet()
        
        # 기본 스타일 업데이트
        styles['Normal'].fontName = font_name
        styles['Normal'].fontSize = 10
        styles['Normal'].leading = 16
        
        styles['Heading1'].fontName = font_name
        styles['Heading1'].fontSize = 24
        styles['Heading1'].leading = 30
        styles['Heading1'].spaceAfter = 20
        
        styles['Heading2'].fontName = font_name
        styles['Heading2'].fontSize = 18
        styles['Heading2'].leading = 24
        styles['Heading2'].spaceBefore = 15
        styles['Heading2'].spaceAfter = 10
        
        styles['Heading3'].fontName = font_name
        styles['Heading3'].fontSize = 14
        styles['Heading3'].leading = 18
        styles['Heading3'].spaceBefore = 10
        
        # 코드 블록 스타일
        code_style = ParagraphStyle(
            name='Code',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9,
            leading=12,
            backColor=colors.lightgrey,
            borderPadding=5,
            spaceAfter=10
        )

        # 3. Markdown -> HTML 변환
        html_content = markdown.markdown(markdown_text)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        story = []
        
        # HTML 요소를 순회하며 ReportLab Flowable로 변환
        # 최상위 요소만 처리 (중첩된 구조는 단순화)
        for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'pre', 'blockquote']):
            if element.name == 'h1':
                story.append(Paragraph(element.get_text(), styles['Heading1']))
            elif element.name == 'h2':
                story.append(Paragraph(element.get_text(), styles['Heading2']))
            elif element.name == 'h3':
                story.append(Paragraph(element.get_text(), styles['Heading3']))
            elif element.name == 'p':
                # 내부 태그(b, i 등) 보존을 위해 decode_contents 사용
                text = element.decode_contents()
                # strong -> b, em -> i 변환 (ReportLab 호환)
                text = text.replace('<strong>', '<b>').replace('</strong>', '</b>')
                text = text.replace('<em>', '<i>').replace('</em>', '</i>')
                text = text.replace('<code>', '<font color="blue">').replace('</code>', '</font>')
                story.append(Paragraph(text, styles['Normal']))
                story.append(Spacer(1, 8))
            elif element.name in ['ul', 'ol']:
                items = []
                for li in element.find_all('li'):
                    text = li.decode_contents()
                    text = text.replace('<strong>', '<b>').replace('</strong>', '</b>')
                    text = text.replace('<em>', '<i>').replace('</em>', '</i>')
                    items.append(ListItem(Paragraph(text, styles['Normal'])))
                
                t = ListFlowable(
                    items, 
                    bulletType='bullet' if element.name == 'ul' else '1',
                    start='circle' if element.name == 'ul' else None,
                    leftIndent=20
                )
                story.append(t)
                story.append(Spacer(1, 8))
            elif element.name == 'pre':
                text = element.get_text()
                story.append(Preformatted(text, code_style))
                story.append(Spacer(1, 8))
            elif element.name == 'blockquote':
                text = element.get_text()
                story.append(Paragraph(f"<i>{text}</i>", styles['Normal'])) # 인용구는 이탤릭으로 처리
                story.append(Spacer(1, 8))

        # 4. PDF 생성
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=A4,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=72
        )
        doc.build(story)
        return True

    except Exception as e:
        print(f"PDF 변환 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def convert_pdf_to_image(pdf_path: str, output_image_path: str = None) -> str:
    """
    PDF 파일의 첫 페이지를 이미지(PNG)로 변환합니다.
    PyMuPDF (fitz)를 사용합니다.
    
    Args:
        pdf_path: 변환할 PDF 파일 경로
        output_image_path: 저장할 이미지 파일 경로 (None일 경우 PDF 경로 기반으로 자동 생성)
        
    Returns:
        str: 생성된 이미지 파일 경로
    """
    try:
        import fitz  # PyMuPDF
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        doc = fitz.open(pdf_path)
        if doc.page_count < 1:
            raise ValueError("PDF has no pages")
            
        # 첫 페이지만 변환
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=150) # 150 DPI로 렌더링
        
        if output_image_path is None:
            output_image_path = os.path.splitext(pdf_path)[0] + ".png"
            
        pix.save(output_image_path)
        doc.close()
        
        return output_image_path
        
    except ImportError:
        print("PyMuPDF (fitz) is not installed. Please install it using 'uv pip install pymupdf'")
        raise
    except Exception as e:
        print(f"PDF to Image conversion failed: {e}")
        raise
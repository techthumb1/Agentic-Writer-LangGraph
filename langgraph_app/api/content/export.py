from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io

router = APIRouter()

def markdown_to_html(content: str) -> str:
    """Convert markdown to HTML"""
    import re
    html = content
    html = re.sub(r'^### (.*)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    html = re.sub(r'\n\n', '</p><p>', html)
    return f'<p>{html}</p>'

@router.post("/content/export")
async def export_content(data: dict):
    """Export content in specified format"""
    title = data.get("title", "Untitled")
    content = data.get("content", "")
    format_type = data.get("format", "markdown")
    
    if format_type == "markdown":
        output = f"# {title}\n\n{content}"
        media_type = "text/markdown"
        filename = f"{title.replace(' ', '_')}.md"
    
    elif format_type == "html":
        html_content = markdown_to_html(content)
        output = f"""<!DOCTYPE html>
<html><head><title>{title}</title></head>
<body><h1>{title}</h1>{html_content}</body></html>"""
        media_type = "text/html"
        filename = f"{title.replace(' ', '_')}.html"
    
    else:
        output = content
        media_type = "text/plain"
        filename = f"{title.replace(' ', '_')}.txt"
    
    return StreamingResponse(
        io.BytesIO(output.encode()),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
from PIL import Image
from pathlib import Path
root=Path(r'D:\STATOBERRY\PAPAYA\KAUMELON')
im=Image.open(root/'analytics/integrations/statistics/images/cover.png').convert('RGB')
im.thumbnail((640,1100),Image.Resampling.LANCZOS)
out=root/'images/UG/agstat-cover-cb9efbe.webp'
im.save(out,'WEBP',quality=88,method=6)
for name in ('index.qmd','bookshelfug.qmd'):
 p=root/name
 text=p.read_text(encoding='utf-8')
 text=text.replace('images/UG/statcover.jpg','images/UG/agstat-cover-cb9efbe.webp').replace('width="360" height="480"',f'width="{im.width}" height="{im.height}"')
 p.write_text(text,encoding='utf-8')
print(f'Cover: {im.width} x {im.height}; {out.stat().st_size:,} bytes')

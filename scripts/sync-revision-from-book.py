"""Select revision material verbatim from the author's textbook, with a source manifest.
Run with --book-path pointing at a checkout of STATOBERRYPAPAYA/TextbookofAgstat.
The source checkout is read only. This never invents summaries, examples or answers.
"""
import argparse,hashlib,html,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();parser.add_argument('--book-path',type=Path,required=True);args=parser.parse_args()
book=args.book_path.resolve();quarto='quarto'
def render(md):
 return subprocess.run([quarto,'pandoc','--from=markdown','--to=html','--mathjax'],input=md,encoding='utf-8',capture_output=True,check=True).stdout.strip()
def section(text,title):
 m=re.search(r'^### '+re.escape(title)+r'[^\n]*\n(.*?)(?=^#{1,3} |\Z)',text,re.M|re.S)
 if not m:return None
 return dict(heading=title,markdown=m.group(1).strip(),start_line=text.count('\n',0,m.start(1))+1,end_line=text.count('\n',0,m.end(1))+1)
def card(title,md,colour='green',extra=''):
 return f'<section class="card c-{colour} {extra}"><h2>{html.escape(title)}</h2><div class="body">{render(md)}</div></section>'
manifest={'repository':'https://github.com/STATOBERRYPAPAYA/TextbookofAgstat','revision':subprocess.check_output(['git','-C',str(book),'rev-parse','HEAD'],text=True).strip(),'policy':'All educational text, formulae, examples, questions and answers below are selected from the corresponding textbook chapter. Only presentation markup and navigation are added.','chapters':[]}
for file in sorted((ROOT/'revision/_src/agstat').glob('*.html')):
 meta=dict(re.findall(r'^(\w+): (.*)$',file.read_text(encoding='utf-8'),re.M));source=book/meta['chapter'].replace('.html','.qmd');text=source.read_text(encoding='utf-8');sections=[];cards=[]
 quick=section(text,'Quick revision');assert quick,source
 sections.append(quick)
 # Every quick-revision bullet is retained, in textbook order.
 bullets=re.findall(r'^[*-] .*?(?=^[*-] |\Z)',quick['markdown'],re.M|re.S)
 if bullets:
  for j in range(0,len(bullets),5):
   cards.append(card('Quick revision'+(f' · {j//5+1}' if len(bullets)>5 else ''),'\n'.join(x.rstrip() for x in bullets[j:j+5]),'green'))
 else:cards.append(card('Quick revision',quick['markdown']))
 formulas=section(text,'Important formulae') or section(text,'Important concepts')
 if formulas:
  sections.append(formulas)
  blocks=re.split(r'\n\s*\n',formulas['markdown']);units=[]
  for block in blocks:
   if block.startswith('$$') or block.lower().startswith(('where','this is','for ')):
    if units:units[-1]+='\n\n'+block
    else:units.append(block)
   else:units.append(block)
  groups=[];current=[];size=0
  for unit in units:
   if current and (size+len(unit)>1000 or len(current)>=3):groups.append('\n\n'.join(current));current=[];size=0
   current.append(unit);size+=len(unit)
  if current:groups.append('\n\n'.join(current))
  for j,group in enumerate(groups):cards.append(card(formulas['heading']+(f' · {j+1}' if len(groups)>1 else ''),group,'blue','book-formulas'))
 # Include one complete short worked example only where it exists in the chapter.
 examples=list(re.finditer(r'^::: \{#(exm[^\n }]+)[^\n]*\}\n(.*?)^:::',text,re.M|re.S))
 for ex in examples:
  md=ex.group(2).strip()
  if len(md)<=1100 and not re.search(r'@|!\[|```|\|',md) and 'Solution' in md:
   sections.append(dict(heading=ex.group(1),markdown=md,start_line=text.count('\n',0,ex.start(2))+1,end_line=text.count('\n',0,ex.end(2))+1))
   cards.append(card('Worked example from the chapter',md,'ochre'));break
 questions=section(text,'Fill in the blanks');answers=section(text,'Answers to fill in the blanks')
 if questions and answers:
  qlist=re.findall(r'^\s*\d+[.)]\s+(.*?)(?=^\s*\d+[.)]\s+|\Z)',questions['markdown'],re.M|re.S)[:4]
  amap=dict(re.findall(r'`(\d+)\.`\s*(.*?)(?=`\d+\.`|\n:::|\Z)',answers['markdown'],re.S))
  if qlist and all(str(i+1) in amap for i in range(len(qlist))):
   sections.extend([questions,answers]);items=[]
   for i,q in enumerate(qlist):items.append('<li>'+re.sub(r'^<p>|</p>$', '', render(q.strip()))+f'<span class="ans">{re.sub(r'^<p>|</p>$', '', render(amap[str(i+1)].strip()))}</span></li>')
   cards.append('<section class="card c-plum fib"><h2>Self-check from the chapter</h2><div class="body"><ol class="fib-list">'+''.join(items)+'</ol><button type="button" class="rv-btn fib-toggle" data-fib-toggle>Show answers</button></div></section>')
 # Save the selected source verbatim alongside its origin. Rendering adds no educational text.
 manifest['chapters'].append(dict(num=int(meta['num']),file=source.name,sha256=hashlib.sha256(source.read_bytes()).hexdigest(),sections=sections))
 meta['sub']='From the chapter’s own revision points, formulae and questions.';meta['motto']='';meta['source_revision']=manifest['revision'][:12]
 header='<!--\n'+'\n'.join(k+':'+(' '+v if v else '') for k,v in meta.items())+'\n-->\n'
 file.write_text(header+'\n\n'.join(cards)+'\n',encoding='utf-8')
 print(meta['num'],source.name,len(cards),'cards selected from textbook')
(ROOT/'revision/_src/agstat/book-sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

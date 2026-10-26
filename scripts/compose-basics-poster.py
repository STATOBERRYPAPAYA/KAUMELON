from pathlib import Path
import re,html,json,csv,hashlib
root=Path(__file__).resolve().parent.parent
book=Path(globals().get('BOOK_PATH',root/'analytics/integrations/statistics')); source=(book/'intro.qmd').read_text(encoding='utf-8');selected=[]
def take(text):
 assert text in source,text[:80]
 selected.append(text)
 return html.escape(re.sub(r'\*([^*]+)\*',r'\1',text.replace('**','')))
def sentence(prefix):
 start=source.index(prefix);end=start+re.search(r'\.(?=\s|$)',source[start:]).end()
 return take(source[start:end])
def card(title,body,klass=''):
 return '<section class="card '+klass+'"><h2>'+title+'</h2><div class="body">'+body+'</div></section>'
flow=['Collection of data','Organization of data or classification of data','Presentation of data','Analysis of data','Interpretation of data']
body=card('Definition','<p>'+take('Statistics is the science which deals with the')+'</p><ol class="steps">'+''.join('<li>'+take(x)+'</li>' for x in flow)+'</ol>')
body+=card('Scope and importance','<p>'+sentence('**Functions of statistics**:')+'</p><p>'+sentence('It supports decision-making')+'</p><p>'+sentence('By applying appropriate statistical methods')+'</p>')
a='**Descriptive statistics**, which deals with summarizing data from a sample or a population using indexes or measures such as the mean or standard deviation etc.'
b='**Inferential statistics**, use a random sample of data taken from a population to describe and make inferences about the population parameters.'
body+=card('Branches of statistics','<div class="tree"><span class="root">Statistics</span><span class="stem"></span><div class="branches"><div class="leaf">'+take(a)+'</div><div class="leaf">'+take(b)+'</div></div></div>')
body+=card('Population and sample','<div class="pair"><div><h3>Population</h3>'+take('A population is the complete group of interest')+'</div><div><h3>Sample</h3>'+take('a sample is a part selected for study.')+'</div></div><p>'+take('A parameter describes a population, while a statistic is calculated from sample observations.')+'</p>')
body+=card('Types of variables','<table><thead><tr><th>Type</th><th>From the textbook</th></tr></thead><tbody>'+''.join('<tr><td><b>'+title+'</b></td><td>'+sentence(prefix)+'</td></tr>' for title,prefix in [('Quantitative','A *quantitative variable* is one'),('Discrete','*Discrete variables* are variables'),('Continuous','*Continuous variables*, on the other hand'),('Categorical','Categorical variables classify')])+'</tbody></table>')
body+=card('Collection of data','<div class="pair"><div><h3>Primary data</h3>'+sentence('Primary data are first-hand, original')+'</div><div><h3>Secondary data</h3>'+sentence('In contrast, secondary data are obtained')+'</div></div>')
scales=[('Nominal','Data measured on the nominal scale consist'),('Ordinal','This means that the categories have a specific rank'),('Interval','On the interval scale, the data points are ordered'),('Ratio','The **ratio scale**')]
# Use the book's exact first sentence for each measurement scale.
body+=card('Measurement scales','<table><tbody>'+''.join('<tr><td><b>'+t+'</b></td><td>'+sentence(p)+'</td></tr>' for t,p in scales)+'</tbody></table>')
steps=['Decide the number of classes you wish to construct','Determine the class width','Set up the individual class limits','Tally the items into the classes','Count the number of items in each class']
body+=card('Constructing a grouped distribution','<ol class="steps">'+''.join('<li>'+take(x)+'</li>' for x in steps)+'</ol>')
rows=list(csv.DictReader((book/'csv/c1e1.csv').open(encoding='utf-8-sig')))
body+=card('Worked table from the book','<p>'+take('an agricultural student measured the lengths of leaves on an oak tree (to the nearest cm).')+'</p><table><thead><tr><th>Class</th><th>Frequency</th></tr></thead><tbody>'+''.join('<tr><td>'+html.escape(r['Class'])+'</td><td>'+r['Frequency']+'</td></tr>' for r in rows)+'</tbody></table><p class="source-note-inline">Source: Chapter 1, frequency distribution table.</p>')
formula_section=re.search(r'^### Important formulae[^\n]*\n(.*?)(?=^### )',source,re.M|re.S).group(1)
formulas=re.findall(r'([^\n]+):\s*\n\s*\$\$(.*?)\$\$',formula_section,re.S)
chosen=[(label.strip(),tex.strip()) for label,tex in formulas if any(k in label.lower() for k in ['sturges','class mark','class width','relative frequency','sum of frequencies']) and 'lower endpoint' not in label.lower()]
body+=card('Important formulae','<div class="fxgrid">'+''.join('<div class="fx"><span class="lbl">'+html.escape(label)+'</span>$$'+html.escape(tex)+'$$</div>' for label,tex in chosen)+'</div>','book-formulas')
body+=card('Key points and limits','<p>'+sentence('**Common limitations of statistics**:')+'</p><p>'+sentence('A large dataset cannot by itself')+'</p><p>'+sentence('Sample results are subject to uncertainty')+'</p>','poster-key')
p=root/'revision/_src/agstat/01-basics-of-statistics.html';old=p.read_text(encoding='utf-8');meta=old[:old.index('-->')+3];p.write_text(meta+'\n'+body+'\n',encoding='utf-8')
manifest_path=root/'revision/_src/agstat/book-sources.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'));manifest['chapters'][0]['poster_excerpts']=selected;manifest['chapters'][0]['poster_data']={'file':'csv/c1e1.csv','sha256':hashlib.sha256((book/'csv/c1e1.csv').read_bytes()).hexdigest()};manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Composed reference-style poster from',len(selected),'verified textbook excerpts.')

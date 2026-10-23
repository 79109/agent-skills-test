"""Render a supplied node/edge layout into an editable, non-scale SVG schematic."""
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

NS='http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def add(parent, tag, attrs=None, text=None):
    e=ET.SubElement(parent, '{'+NS+'}'+tag, {k:str(v) for k,v in (attrs or {}).items()})
    e.text=text
    return e


def finite(x):
    x=float(x)
    if not math.isfinite(x):
        raise ValueError('Coordinates and dimensions must be finite.')
    return x


def render(data):
    width=finite(data.get('width', 960))
    height=finite(data.get('height', 600))
    if width < 200 or height < 160:
        raise ValueError('Canvas must be at least 200 by 160.')
    nodes=data.get('nodes',[])
    if not nodes:
        raise ValueError('Supply nodes with explicit display coordinates.')
    lookup={}
    for n in nodes:
        key=n['id']
        if not isinstance(key,str) or not key or key in lookup:
            raise ValueError('Node IDs must be unique non-empty strings.')
        x,y=finite(n['x']),finite(n['y'])
        w,h=finite(n.get('width',120)),finite(n.get('height',48))
        if w<=0 or h<=0 or x-w/2<8 or x+w/2>width-8 or y-h/2<65 or y+h/2>height-40:
            raise ValueError(f'Node {key} is outside the usable canvas; adjust the layout.')
        lookup[key]={'x':x,'y':y,'width':w,'height':h,'label':str(n.get('label',key))}
    edges=data.get('edges',[])
    for e in edges:
        if e['from'] not in lookup or e['to'] not in lookup or e['from']==e['to']:
            raise ValueError('Edges need distinct, existing node endpoints.')
        if 'directed' in e and type(e['directed']) is not bool:
            raise ValueError('directed must be true or false.')
    svg=ET.Element('{'+NS+'}svg',{'width':str(width),'height':str(height),'viewBox':f'0 0 {width} {height}'})
    add(svg,'title',text=str(data.get('title','工程关系示意')))
    add(svg,'rect',{'width':width,'height':height,'fill':'white'})
    defs=add(svg,'defs')
    marker=add(defs,'marker',{'id':'arrow','markerWidth':10,'markerHeight':8,'refX':9,'refY':4,'orient':'auto','markerUnits':'userSpaceOnUse'})
    add(marker,'path',{'d':'M 0 0 L 10 4 L 0 8 Z','fill':'#334155'})
    text_style={'font-family':'Microsoft YaHei, Noto Sans CJK SC, sans-serif','fill':'#1e293b'}
    add(svg,'text',{**text_style,'x':24,'y':34,'font-size':20},str(data.get('title','工程关系示意')))
    def end(n, dx, dy):
        tx=n['width']/2/abs(dx) if dx else float('inf')
        ty=n['height']/2/abs(dy) if dy else float('inf')
        scale=min(tx,ty)
        return n['x']+dx*scale,n['y']+dy*scale
    for e in edges:
        a,b=lookup[e['from']],lookup[e['to']]
        dx,dy=b['x']-a['x'],b['y']-a['y']
        if dx==0 and dy==0:
            raise ValueError('Connected nodes cannot share the same center.')
        x1,y1=end(a,dx,dy)
        x2,y2=end(b,-dx,-dy)
        line={'x1':x1,'y1':y1,'x2':x2,'y2':y2,'stroke':'#334155','stroke-width':2}
        if e.get('directed',False):line['marker-end']='url(#arrow)'
        add(svg,'line',line)
        if e.get('label'):
            add(svg,'text',{**text_style,'x':(x1+x2)/2,'y':(y1+y2)/2-9,'text-anchor':'middle','font-size':13},str(e['label']))
    for n in lookup.values():
        add(svg,'rect',{'x':n['x']-n['width']/2,'y':n['y']-n['height']/2,'width':n['width'],'height':n['height'],
                        'rx':5,'fill':'#eff6ff','stroke':'#2563eb','stroke-width':1.5})
        add(svg,'text',{**text_style,'x':n['x'],'y':n['y']+5,'text-anchor':'middle','font-size':15},n['label'])
    add(svg,'text',{**text_style,'x':24,'y':height-16,'font-size':12},'非比例示意；节点位置仅用于图面布局')
    return ET.tostring(svg,encoding='unicode',xml_declaration=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    try:
        output=render(json.loads(a.input.read_text(encoding='utf-8-sig')))
        a.output.parent.mkdir(parents=True,exist_ok=True)
        with a.output.open('x',encoding='utf-8') as f:f.write(output+'\n')
    except (ValueError,KeyError,TypeError,OSError) as exc:
        p.exit(2,f'Error: {exc}\n')


if __name__=='__main__':main()

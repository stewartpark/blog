from nbconvert import HTMLExporter
from jinja2 import Environment, FileSystemLoader
from functools import reduce
import nbformat
import os
import re
from datetime import datetime

title_re = re.compile(r'# TITLE: (.+?)[\n\r]')
cover_re = re.compile(r'# COVER: (.+?)[\n\r]')
date_re = re.compile(r'# DATE: (.+?)[\n\r]')
tags_re = re.compile(r'# TAGS: (.+?)[\n\r]')

def parse_metadata(s):
    title = title_re.findall(s)
    cover = cover_re.findall(s)
    date = date_re.findall(s)
    tags = tags_re.findall(s)
    return \
      title[0], \
      cover[0], \
      date[0], \
      (tags[0].split(',') if tags else [])

def read_notebooks():
    exporter = HTMLExporter()
    exporter.template_file = 'basic'
    paths = sorted(filter(lambda x: x.endswith(".ipynb"), os.listdir('notebooks')))
    notebooks = []
    for path in paths:
        with open("notebooks/{}".format(path)) as f:
            notebook = nbformat.read(f, as_version=4)
            title, cover, date, tags = parse_metadata(notebook.cells[0]['source'])
            body, resources = exporter.from_notebook_node(notebook)
            name = path.rsplit('.', 1)[0].lower().replace(' ', '-')
            notebooks.append({
                'name': name,
                'title': title,
                'cover': cover,
                'date': datetime.strptime(date, '%Y-%m-%d'),
                'tags': tags,
                'path': '/notebooks/{}.html'.format(name),
                'html': body
            })
    notebooks = list(reversed(sorted(notebooks, key=lambda x: x['date'])))
    return notebooks

def create_directories():
    try:
        os.mkdir('docs')
    except:
        pass
    try:
        os.mkdir('docs/notebooks')
    except:
        pass
    try:
        os.mkdir('docs/tags')
    except:
        pass
    try:
        os.mkdir('docs/assets')
    except:
        pass

    
if __name__ == '__main__':
    notebooks = read_notebooks()
    tags = sorted(list(set(reduce(lambda a, b: a + b, [x['tags'] for x in notebooks]))))
    create_directories()
    env = Environment(loader=FileSystemLoader(("templates/")))
    context = { 'notebooks': notebooks, 'tags': tags }
    # Index
    with open('templates/index.html') as f:
        tmpl = env.from_string(f.read())
        with open('docs/index.html', 'w') as o:
            o.write(tmpl.render(**context))

    # Tags
    for tag in tags:
        with open('templates/index.html') as f:
            tmpl = env.from_string(f.read())
        nbs = [nb for nb in notebooks if tag in nb['tags']]
        with open('docs/tags/{}.html'.format(tag), 'w') as o:
            o.write(tmpl.render(current_tag=tag, notebooks=nbs, tags=tags))

    # Notebooks
    with open('templates/notebook.html', 'r') as f:
        tmpl = env.from_string(f.read())
        for notebook in notebooks:
            with open('docs/notebooks/{}.html'.format(notebook['name']), 'wb') as o:
                o.write(tmpl.render(notebook=notebook, **context).encode('utf-8'))
                

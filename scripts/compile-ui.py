"""Compile the existing design into a Next-owned presentation tree.

Run while legacy HTML still exists. The generated tree has no Django runtime
or template-loader dependency. Django exports view data; Next renders the UI.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'({%.*?%}|{{.*?}}|{#.*?#})', re.S)


def compile_source(source):
    # HTML comments carry no UI; discard commented examples/dead scripts.
    source = re.sub(r'<!--.*?-->', '', source, flags=re.S)
    tokens = [token for token in TOKEN.split(source) if token]
    position = 0

    def read(stops=()):
        nonlocal position
        nodes = []
        while position < len(tokens):
            token = tokens[position]
            if token.startswith('{%'):
                instruction = token[2:-2].strip()
                parts = instruction.split(None, 1)
                tag = parts[0]
                args = parts[1].strip() if len(parts) > 1 else ''
                if tag in stops:
                    return nodes, tag, args
                position += 1
                if tag == 'if':
                    branches = []
                    while True:
                        body, end, rest = read(('elif', 'else', 'endif'))
                        branches.append({'test': args, 'body': body})
                        position += 1
                        if end == 'elif':
                            args = rest
                            continue
                        if end == 'else':
                            body, _, _ = read(('endif',))
                            branches.append({'test': None, 'body': body})
                            position += 1
                        break
                    nodes.append({'op': 'if', 'branches': branches})
                elif tag in ('for', 'block', 'with', 'blocktrans', 'comment'):
                    ends = {'for': ('empty', 'endfor'), 'block': ('endblock',), 'with': ('endwith',), 'blocktrans': ('endblocktrans',), 'comment': ('endcomment',)}
                    body, end, _ = read(ends[tag])
                    position += 1
                    empty = []
                    if end == 'empty':
                        empty, _, _ = read(('endfor',))
                        position += 1
                    if tag != 'comment':
                        nodes.append({'op': tag, 'args': args, 'body': body, 'empty': empty})
                elif tag != 'load':
                    nodes.append({'op': tag, 'args': args})
            elif token.startswith('{{'):
                nodes.append({'op': 'value', 'expr': token[2:-2].strip()})
                position += 1
            elif token.startswith('{#'):
                position += 1
            else:
                nodes.append({'op': 'text', 'text': token})
                position += 1
        return nodes, '', ''
    return read()[0]


def main():
    templates = {}
    for folder in [ROOT / 'templates', *sorted(ROOT.glob('*/templates'))]:
        for source in sorted(folder.rglob('*.html')):
            name = source.relative_to(folder).as_posix()
            if name in templates:
                raise ValueError(f'Duplicate presentation name: {name}')
            templates[name] = compile_source(source.read_text())
    out = ROOT / 'frontend/ui/presentation.json'
    out.write_text(json.dumps(templates, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(f'Compiled {len(templates)} presentations into {out.relative_to(ROOT)}')


if __name__ == '__main__':
    main()

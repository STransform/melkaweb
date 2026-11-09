'use client';
import { useEffect, useRef, useState, type MouseEvent } from 'react';

const tools = [
  ['Heading', '\n## ', 'Section title', '\n'], ['Bold', '**', 'important text', '**'],
  ['Code', '\n```python\n', 'print("Hello, Melka!")', '\n```\n'],
  ['Link', '[', 'link text', '](https://example.com)'], ['List', '\n- ', 'First step', '\n- Second step\n'],
  ['Callout', '\n> **Note:** ', 'Helpful context for your reader.', '\n'],
  ['Table', '\n| Setting | Value |\n| --- | --- |\n| ', 'PORT', ' | 8000 |\n'],
] as const;
const codeSamples:Record<string,string>={python:'print("Hello, Melka!")',java:'System.out.println("Hello, Melka!");',javascript:'console.log("Hello, Melka!");',typescript:'console.log("Hello, Melka!");',bash:'echo "Hello, Melka!"',yaml:'name: melka',json:'{ "name": "melka" }',sql:'SELECT * FROM tutorials;',dockerfile:'FROM python:3.12-slim',plaintext:'Your code here'};

export default function TutorialEditor({ name, id, initial, draftKey, required=false }: { name:string; id:string; initial:string; draftKey:string; required?:boolean }) {
  const [value, setValue] = useState(initial);
  const [preview, setPreview] = useState<string | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewBusy, setPreviewBusy] = useState(false);
  const [language, setLanguage] = useState('python');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const input = useRef<HTMLTextAreaElement>(null);
  const imageInput = useRef<HTMLInputElement>(null);
  const currentValue = useRef(initial);
  const selection = useRef({start: initial.length, end: initial.length});
  useEffect(()=>{
    try {const saved=localStorage.getItem(draftKey);if(saved && saved!==initial)setNotice('An unsaved browser backup is available. Choose Restore browser backup to recover it.');}catch{/* Browser storage may be unavailable. */}
  },[draftKey,initial]);
  function rememberSelection() {
    if (input.current) selection.current={start:input.current.selectionStart,end:input.current.selectionEnd};
  }
  function update(next:string) {
    currentValue.current=next;
    setValue(next);
    try { localStorage.setItem(draftKey, next); setNotice('Writing backed up in this browser. Use Save draft to save it to Melka.'); } catch { /* Storage may be disabled. */ }
  }
  function insert(before:string, placeholder:string, after:string) {
    const element = input.current;
    const source = currentValue.current;
    const start = Math.min(element?.selectionStart ?? selection.current.start,source.length), end = Math.min(element?.selectionEnd ?? selection.current.end,source.length);
    const selected = source.slice(start, end) || placeholder;
    update(source.slice(0,start) + before + selected + after + source.slice(end));
    setPreviewOpen(true);
    selection.current={start:start+before.length,end:start+before.length+selected.length};
    requestAnimationFrame(() => { element?.focus({preventScroll:true}); element?.setSelectionRange(selection.current.start,selection.current.end); });
  }
  useEffect(() => {
    if (!previewOpen) return;
    const controller = new AbortController();
    const timer=setTimeout(async () => {
      setPreviewBusy(true);
      try {
        const format = input.current?.form?.querySelector<HTMLSelectElement>('[name=content_format]')?.value || 'markdown';
        const response = await fetch('/tutorial-preview/', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({content:value,format}), signal:AbortSignal.any([controller.signal,AbortSignal.timeout(15000)])});
        if (!response.ok) throw new Error('Unable to render preview.');
        setPreview((await response.json()).html);
      } catch {
        if (!controller.signal.aborted) setNotice('Unable to load preview. Your writing is still here. Please try Preview again.');
      } finally { if (!controller.signal.aborted) setPreviewBusy(false); }
    },250);
    return () => {clearTimeout(timer);controller.abort();};
  },[value,previewOpen]);
  async function upload(file?:File) {
    if (!file) return;
    setBusy(true);
    try {
      const {csrfToken} = await fetch('/api/frontend/csrf/',{cache:'no-store',signal:AbortSignal.timeout(15000)}).then(r => r.json());
      const body = new FormData(); body.set('image',file);
      const response = await fetch('/api/frontend/tutorial-images/',{method:'POST',headers:{'X-CSRFToken':csrfToken},body,signal:AbortSignal.timeout(20000)});
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Upload failed.');
      insert('\n![', 'Describe this screenshot', `](${data.url})\n`);
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Upload failed.'); }
    finally { setBusy(false); }
  }
  async function copyPreviewCode(event:MouseEvent<HTMLElement>) {
    const target=event.target;
    if (!(target instanceof Element)) return;
    const button=target.closest<HTMLButtonElement>('[data-copy-tutorial-code]');
    if (!button) return;
    const code=button.closest('.tutorial-code-block')?.querySelector('pre code');
    if (!code) return;
    try {
      await navigator.clipboard.writeText(code.textContent || '');
      button.textContent='Copied!';
      setTimeout(()=>{if(button.isConnected)button.textContent='Copy code';},1800);
    } catch {setNotice('Clipboard unavailable. Select and copy the code manually.');}
  }
  return <div className="tutorial-editor" data-uploading={busy}>
    <p style={{fontSize:13,color:'#536a80'}}>Select text and choose a formatting tool. The editor inserts Markdown, and the live preview shows how readers will see it. Your text is saved to Melka when you choose Save draft or Publish tutorial.</p>
    <div style={{display:'flex',flexWrap:'wrap',gap:6,marginBottom:10}} role="toolbar" aria-label="Tutorial formatting">
      {tools.map(([label,before,placeholder,after]) => <button className="btn btn-sm btn-light" type="button" key={label} title={`Insert ${label.toLowerCase()} formatting`} onPointerDown={e=>e.preventDefault()} onClick={()=>insert(label==='Code'?`\n\`\`\`${language}\n`:before,label==='Code'?codeSamples[language]:placeholder,after)}>{label}</button>)}
      <select aria-label="Code language" value={language} onChange={e=>setLanguage(e.target.value)} className="form-select form-select-sm" style={{width:'auto'}}>{['python','java','javascript','typescript','bash','yaml','json','sql','dockerfile','plaintext'].map(lang=><option value={lang} key={lang}>{lang}</option>)}</select>
      <button className="btn btn-sm btn-light" type="button" disabled={busy} onClick={()=>imageInput.current?.click()}>{busy?'Uploading…':'Upload screenshot'}</button>
      <input ref={imageInput} type="file" aria-label="Screenshot file" accept="image/png,image/jpeg,image/webp,image/gif" disabled={busy} onChange={e=>{void upload(e.target.files?.[0]); e.target.value='';}} hidden />
      <button className="btn btn-sm btn-outline-primary" type="button" aria-pressed={previewOpen} onClick={()=>{setPreviewOpen(true);}}>{previewBusy?'Rendering…':'Preview'}</button>
      {previewOpen && <button className="btn btn-sm btn-light" type="button" onClick={()=>setPreviewOpen(false)}>Hide preview</button>}
      <button className="btn btn-sm btn-light" type="button" onClick={()=>{try { const saved=localStorage.getItem(draftKey); if(saved!==null){currentValue.current=saved;setValue(saved);selection.current={start:saved.length,end:saved.length};setNotice('Browser backup restored.');}else setNotice('No browser backup found.'); } catch {setNotice('Browser storage unavailable.');}}}>Restore browser backup</button>
    </div>
    <textarea ref={input} id={id} name={name} className="form-control" rows={18} required={required} value={value} onSelect={rememberSelection} onBlur={rememberSelection} onChange={e=>{update(e.target.value);rememberSelection();}} style={{fontFamily:'ui-monospace,monospace',fontSize:14,lineHeight:1.8,tabSize:2}} />
    <small style={{display:'block',marginTop:8,color:'#60748a'}}>{value.trim().split(/\s+/).filter(Boolean).length} words · approximately {Math.max(1,Math.ceil(value.trim().split(/\s+/).length/200))} min read</small>
    <p role="status" style={{fontSize:13,marginTop:8}}>{notice}</p>
    {previewOpen && <section className="tutorial-portal tutorial-editor-preview" aria-label="Tutorial preview" aria-busy={previewBusy} onClick={event=>void copyPreviewCode(event)}><header className="tutorial-preview-header"><div><span className="tutorial-preview-eyebrow">LIVE PREVIEW</span><h3>Reader preview</h3></div><span className="tutorial-preview-status">{previewBusy?'Updating…':'Ready'}</span></header>{preview!==null ? <div className="tutorial-prose" dangerouslySetInnerHTML={{__html:preview}} /> : <p>Rendering preview…</p>}</section>}
  </div>;
}

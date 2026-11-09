/*
 * UI-preserving React presentation evaluator. The compiled tree belongs to
 * Next.js; Django supplies structured data and validates all mutations.
 * Original CSS/classes and scripts are retained so migration does not redesign
 * the site. There is no Django template rendering in this frontend path.
 */
import trees from '../../ui/presentation.json' with { type: 'json' };
import { homeHero } from './home-hero.mjs';
import { homeAbout } from './home-about.mjs';
import { serviceCards } from './services.mjs';
import { tutorialNodes, recentTutorialNodes } from './tutorials.mjs';

const heroTemplate = 'front/landing_page/01hero_carousel.html';
const heroNodes = homeHero(trees[heroTemplate]);
const aboutTemplate = 'front/landing_page/02stats_section.html';
const aboutNodes = homeAbout(trees[aboutTemplate]);
const serviceOverrides = {
  'front/landing_page/03our_services.html': serviceCards(),
  'front/services_page/02cards.html': serviceCards('services', false),
};

const safe = html => ({ $safe: String(html ?? '') });
const isSafe = value => value && typeof value === 'object' && '$safe' in value;
export const escape = value => String(value ?? '').replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;' })[ch]);
const words = input => input.match(/"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[^\s]+/g) || [];
const split = (input, delimiter) => {
  const out = []; let value = '', quote = '';
  for (let i = 0; i < input.length; i++) {
    const ch = input[i];
    if (quote) { value += ch; if (ch === quote && input[i - 1] !== '\\') quote = ''; }
    else if (ch === '"' || ch === "'") { quote = ch; value += ch; }
    else if (ch === delimiter) { out.push(value); value = ''; }
    else value += ch;
  }
  out.push(value); return out;
};
const items = value => Array.isArray(value) ? value : value?.$items || value?.$form || [];
const truth = value => value?.$truth !== undefined ? value.$truth : Array.isArray(value) ? value.length > 0 : value && typeof value === 'object' ? Object.keys(value).length > 0 : !!value;
const label = value => isSafe(value) ? value.$safe : value?.$label !== undefined ? value.$label : value == null ? '' : typeof value === 'object' ? '' : String(value);
const equal = (a, b) => a === b || (a?.$model && b?.$model && a.$model === b.$model && a.id === b.id);
function errorsHtml(errors) { return errors?.length ? `<ul class="errorlist">${errors.map(error => `<li>${escape(error)}</li>`).join('')}</ul>` : ''; }
function attributes(attrs) { return Object.entries(attrs).filter(([, value]) => value != null && value !== false).map(([key, value]) => value === true ? ` ${escape(key)}` : ` ${escape(key)}="${escape(value)}"`).join(''); }
function fieldHtml(field) {
  const attrs = { ...field.attrs, name: field.name, id: field.id, required: field.required && !(field.type === 'file' && field.value), disabled: field.disabled };
  if (field.errors?.length) attrs['aria-invalid'] = 'true';
  const value = field.value ?? '';
  if (field.select) {
    const selected = new Set((Array.isArray(value) ? value : [value]).map(String));
    return `<select${attributes({ ...attrs, multiple: field.multiple })}>${field.choices.map(([key, title]) => `<option value="${escape(key)}"${selected.has(key) ? ' selected' : ''}>${escape(title)}</option>`).join('')}</select>`;
  }
  if (field.textarea) return `<textarea${attributes(attrs)}>${escape(value)}</textarea>`;
  const input = `<input${attributes({ ...attrs, type: field.type, value: field.type === 'file' ? undefined : field.type === 'checkbox' ? undefined : value, checked: field.type === 'checkbox' ? truth(value) : undefined })}>`;
  if (field.type === 'file' && value) return `Currently: <a href="${escape(value)}">${escape(field.file_name || value)}</a>${field.clearable ? ` <input type="checkbox" name="${escape(field.clear_name)}" id="${escape(field.clear_name)}_id"><label for="${escape(field.clear_name)}_id">Clear</label>` : ''}<br>Change: ${input}`;
  return input;
}
function formHtml(form, layout = 'as_table') {
  return form.$form.map(field => {
    const label = `<label for="${escape(field.id)}">${escape(field.label)}:</label>`;
    const help = field.help_text ? `<span class="helptext">${field.help_text}</span>` : '';
    const body = `${errorsHtml(field.errors)}${fieldHtml(field)}${help}`;
    return layout === 'as_p' ? `<p>${label} ${body}</p>` : layout === 'as_ul' ? `<li>${label} ${body}</li>` : `<tr><th>${label}</th><td>${body}</td></tr>`;
  }).join('');
}
function display(value) {
  if (isSafe(value)) return value.$safe;
  if (value?.$field) return fieldHtml(value);
  if (value?.$form) return formHtml(value);
  if (Array.isArray(value)) return escape(value.join(', '));
  return escape(label(value));
}
function lookup(path, ctx) {
  let value = ctx;
  for (const part of path.split('.')) {
    if (part === '__proto__' || part === 'constructor' || part === 'prototype' || part.startsWith('_')) return undefined;
    if (value == null) return undefined;
    if (value?.$form && ['as_p', 'as_table', 'as_ul'].includes(part)) value = safe(formHtml(value, part));
    else if (value?.$field && part === 'label_tag') value = safe(`<label for="${escape(value.id)}">${escape(value.label)}:</label>`);
    else if (Array.isArray(value) && part === 'all') value = value;
    else if ((Array.isArray(value) || value?.$items) && part === 'count') value = items(value).length;
    else if (part === 'items' && typeof value === 'object' && !Array.isArray(value)) value = Object.entries(value);
    else if (part === 'all' && Array.isArray(value?.$items)) value = value.$items;
    else value = value[part];
  }
  return value;
}
function atom(expr, ctx) {
  if (!expr) return '';
  if ((expr[0] === '"' && expr.at(-1) === '"') || (expr[0] === "'" && expr.at(-1) === "'")) return expr.slice(1, -1).replace(/\\(["'])/g, '$1');
  if (/^-?\d+(\.\d+)?$/.test(expr)) return Number(expr);
  if (['True', 'true'].includes(expr)) return true;
  if (['False', 'false'].includes(expr)) return false;
  if (['None', 'null'].includes(expr)) return null;
  return lookup(expr, ctx);
}
function djangoDate(value, format = 'N j, Y') {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return label(value);
  const values = Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone: 'Africa/Nairobi', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false, weekday: 'long' }).formatToParts(date).map(part => [part.type, part.value]));
  const map = { Y: values.year, y: values.year.slice(-2), m: String(date.getMonth()+1).padStart(2,'0'), n: String(date.getMonth()+1), F: values.month, M: values.month.slice(0,3), N: values.month.slice(0,3), d: values.day.padStart(2,'0'), j: values.day, D: values.weekday.slice(0,3), l: values.weekday, H: values.hour, i: values.minute, s: String(date.getSeconds()).padStart(2,'0'), h: String(Number(values.hour)%12 || 12).padStart(2,'0'), A: Number(values.hour)<12?'AM':'PM' };
  return format.replace(/[YymnFMNdjDlHishA]/g, char => map[char] || char);
}
export function evaluate(expr, ctx) {
  const [base, ...filters] = split(expr.trim(), '|');
  let value = atom(base.trim(), ctx);
  for (const filter of filters) {
    const [name, ...args] = split(filter, ':');
    const arg = args.length ? atom(args.join(':'), ctx) : undefined;
    switch (name) {
      case 'safe': value = safe(label(value)); break;
      case 'default': if (!truth(value)) value = arg; break;
      case 'default_if_none': if (value == null) value = arg; break;
      case 'length': value = typeof value === 'string' ? value.length : items(value).length; break;
      case 'first': value = items(value)[0]; break;
      case 'lower': value = label(value).toLowerCase(); break;
      case 'upper': value = label(value).toUpperCase(); break;
      case 'urlencode': value = encodeURIComponent(label(value)); break;
      case 'formalize': value = label(value).replaceAll('_', ' ').replace(/^./, ch => ch.toUpperCase()); break;
      case 'truncatechars': { const string = label(value); value = string.length > Number(arg) ? string.slice(0, Math.max(0, Number(arg)-1))+'…' : string; break; }
      case 'date': value = djangoDate(value, arg); break;
      case 'floatformat': value = Number(value || 0).toFixed(Number(arg ?? 1)); break;
      case 'divisibleby': value = Number(value) % Number(arg) === 0; break;
      case 'get_key_tasks': value = label(value?.key_tasks).split('\n').filter(Boolean); break;
      case 'get_file_name': value = label(value).split('/').pop(); break;
      case 'linebreaks': value = safe(label(value).split(/\n\n+/).map(part => `<p>${escape(part).replaceAll('\n','<br>')}</p>`).join('\n\n')); break;
      case 'escapejs': value = label(value).replace(/[\\'"<>&=;\-`\u2028\u2029\r\n]/g, ch => '\\u'+ch.charCodeAt(0).toString(16).padStart(4,'0')); break;
      default: throw new Error(`Unsupported presentation filter: ${name}`);
    }
  }
  return value;
}
function condition(expression, ctx) {
  const tokens = expression.match(/"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|==|!=|>=|<=|>|<|\(|\)|[^\s()]+/g) || [];
  let position = 0;
  function primary() {
    if (tokens[position] === '(') { position++; const value = or(); position++; return value; }
    return evaluate(tokens[position++] || '', ctx);
  }
  function comparison() {
    let left = primary();
    const op = tokens[position];
    if (['==','!=','>','<','>=','<=','in','is'].includes(op) || (op === 'not' && tokens[position+1] === 'in')) {
      position++;
      let operation = op;
      if (op === 'not' || (op === 'is' && tokens[position] === 'not')) { operation += ' '+tokens[position++]; }
      const right = primary();
      if (operation === '==' || operation === 'is') left = equal(left,right);
      else if (operation === '!=' || operation === 'is not') left = !equal(left,right);
      else if (operation === '>') left = left > right;
      else if (operation === '<') left = left < right;
      else if (operation === '>=') left = left >= right;
      else if (operation === '<=') left = left <= right;
      else { const contains = Array.isArray(right) ? right.some(item => equal(left,item)) : typeof right === 'string' ? right.includes(label(left)) : !!right && label(left) in right; left = operation === 'not in' ? !contains : contains; }
    }
    return left;
  }
  function not() { if (tokens[position] === 'not') { position++; return !truth(not()); } return comparison(); }
  function and() { let value = not(); while (tokens[position] === 'and') { position++; const right = not(); value = truth(value) && truth(right); } return value; }
  function or() { let value = and(); while (tokens[position] === 'or') { position++; const right = and(); value = truth(value) || truth(right); } return value; }
  return truth(or());
}

export function renderPresentation(payload) {
  const { template, context, routes = {}, translations = {}, csrfToken = '', language = 'en' } = payload;
  const state = { cycle: 0 };
  const t = value => translations[value] ?? value;
  function renderTemplate(name, ctx, overrides = {}) {
    const nodes = ['front/blog.html', 'front/blog_detail.html'].includes(name) && (ctx.tutorial || ctx.tutorial_library)
      ? tutorialNodes(ctx, csrfToken)
      : name === 'front/landing_page/09recent_blogs.html' ? recentTutorialNodes(ctx)
      : serviceOverrides[name] || (name === heroTemplate ? heroNodes : name === aboutTemplate ? aboutNodes : trees[name]);
    if (!nodes) throw new Error(`Unknown presentation: ${name}`);
    const parent = nodes.find(node => node.op === 'extends');
    if (parent) {
      const blocks = {};
      for (const node of nodes) if (node.op === 'block') blocks[node.args.split(' ')[0]] = node.body;
      return renderTemplate(evaluate(parent.args, ctx), ctx, { ...blocks, ...overrides });
    }
    return render(nodes, ctx, overrides);
  }
  function render(nodes, ctx, overrides) {
    let html = '';
    for (const node of nodes) {
      switch (node.op) {
        case 'text': html += node.text; break;
        case 'value': {
          const value = evaluate(node.expr, ctx);
          if (node.expr.endsWith('.errors') || node.expr.endsWith('.non_field_errors')) html += errorsHtml(value);
          else html += display(value);
          break;
        }
        case 'block': html += render(overrides[node.args.split(' ')[0]] || node.body, ctx, overrides); break;
        case 'include': html += renderTemplate(evaluate(words(node.args)[0], ctx), ctx); break;
        case 'if': { const branch = node.branches.find(branch => branch.test === null || condition(branch.test, ctx)); if (branch) html += render(branch.body, ctx, overrides); break; }
        case 'for': {
          const match = node.args.match(/^(.*?)\s+in\s+(.*?)(\s+reversed)?$/);
          if (!match) throw new Error(`Invalid loop: ${node.args}`);
          const names = match[1].split(',').map(name => name.trim());
          let list = items(evaluate(match[2], ctx));
          if (match[3]) list = [...list].reverse();
          if (!list.length) html += render(node.empty, ctx, overrides);
          for (const [index, item] of list.entries()) {
            const child = { ...ctx, forloop: { counter: index+1, counter0: index, revcounter: list.length-index, revcounter0: list.length-index-1, first: index===0, last: index===list.length-1, parentloop: ctx.forloop } };
            names.forEach((name, i) => { child[name] = names.length === 1 ? item : item[i]; });
            html += render(node.body, child, overrides);
          }
          break;
        }
        case 'with': {
          const child = { ...ctx };
          for (const token of words(node.args)) { const index = token.indexOf('='); if (index > 0) child[token.slice(0,index)] = evaluate(token.slice(index+1),ctx); }
          html += render(node.body, child, overrides); break;
        }
        case 'static': { const args = words(node.args); const path = '/static/'+label(evaluate(args[0],ctx)); if (args[1] === 'as') ctx[args[2]] = path; else html += escape(path); break; }
        case 'url': {
          const args = words(node.args); const name = label(evaluate(args.shift(),ctx));
          let path = routes[name];
          if (!path) throw new Error(`Missing route: ${name}`);
          const parameters = [...path.matchAll(/\{([^}]+)\}/g)].map(match => match[1]);
          let index = 0;
          for (let i=0;i<args.length;i++) {
            if (args[i] === 'as') break;
            const equal = args[i].indexOf('=');
            const key = equal > 0 ? args[i].slice(0,equal) : parameters[index++];
            const value = evaluate(equal > 0 ? args[i].slice(equal+1) : args[i],ctx);
            path = path.replace(`{${key}}`,encodeURIComponent(label(value)));
          }
          if (args.at(-2) === 'as') ctx[args.at(-1)] = path;
          else html += escape(path);
          break;
        }
        case 'trans': case 'translate': { const args = words(node.args); const value = t(label(evaluate(args[0],ctx))); if (args.at(-2)==='as') ctx[args.at(-1)] = value; else html += escape(value); break; }
        case 'blocktrans': { let value = node.body.map(part => part.text || '').join(''); if (node.args.includes('trimmed')) value = value.trim().replace(/\s+/g,' '); html += escape(t(value)); break; }
        case 'csrf_token': html += `<input type="hidden" name="csrfmiddlewaretoken" value="${escape(csrfToken)}">`; break;
        case 'get_field_attr': { const args = words(node.args); let value = evaluate(args[0],ctx)?.[label(evaluate(args[1],ctx))]; if (typeof value === 'string' && value.length>25) value=value.slice(0,25)+'...'; html += display(value); break; }
        case 'get_task_count_by_status': html += String(ctx.task_counts?.[evaluate(node.args,ctx)] || 0); break;
        case 'get_current_language': ctx[words(node.args).at(-1)] = language; break;
        case 'get_available_languages': ctx[words(node.args).at(-1)] = [['en','English'],['ax','Amharic'],['ox','Afaan Oromoo']]; break;
        case 'get_language_info_list': ctx[words(node.args).at(-1)] = [{code:'en',name_local:'English'},{code:'ax',name_local:'አማርኛ'},{code:'ox',name_local:'Afaan Oromoo'}]; break;
        case 'cycle': { const args = words(node.args); html += escape(evaluate(args[state.cycle++ % args.length],ctx)); break; }
        case 'now': html += escape(djangoDate(new Date(), evaluate(node.args,ctx))); break;
        case 'placeholder': html += ctx.cms_placeholders?.[evaluate(node.args,ctx)] || ''; break;
        case 'cms_toolbar': html += ctx.cms_toolbar || ''; break;
        case 'render_block': html += (ctx.cms_assets?.[evaluate(node.args,ctx)] || []).join('\n'); break;
        default: throw new Error(`Unsupported presentation operation: ${node.op}`);
      }
    }
    return html;
  }
  return renderTemplate(template, { ...context });
}

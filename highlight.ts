/**
 * হালকা পাইথন সিনট্যাক্স হাইলাইটার (লাইন-ভিত্তিক, সার্ভার/ক্লায়েন্ট উভয়ে চলে)
 */
export function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

const KEYWORDS = new Set([
  "def",
  "class",
  "return",
  "if",
  "elif",
  "else",
  "for",
  "while",
  "import",
  "from",
  "as",
  "with",
  "try",
  "except",
  "finally",
  "raise",
  "pass",
  "break",
  "continue",
  "and",
  "or",
  "not",
  "in",
  "is",
  "None",
  "True",
  "False",
  "lambda",
  "global",
  "assert",
  "yield",
  "async",
  "await",
  "del",
  "nonlocal",
]);

const BUILTINS = new Set([
  "print",
  "len",
  "str",
  "int",
  "float",
  "abs",
  "set",
  "list",
  "dict",
  "tuple",
  "sum",
  "max",
  "min",
  "range",
  "isinstance",
  "enumerate",
  "bool",
  "round",
]);

const SEGMENT_RE =
  /#[^\n]*|"""[\s\S]*?"""|'''[\s\S]*?'''|[bfru]{0,2}"(?:\\.|[^"\\\n])*"|[bfru]{0,2}'(?:\\.|[^'\\\n])*'|@[A-Za-z_][\w.]*|\b[A-Za-z_]\w*\b|\b\d+(?:\.\d+)?\b/g;

function highlightSegment(line: string): string {
  let out = "";
  let last = 0;
  let match: RegExpExecArray | null;
  SEGMENT_RE.lastIndex = 0;

  while ((match = SEGMENT_RE.exec(line)) !== null) {
    if (match.index > last) out += escapeHtml(line.slice(last, match.index));
    const token = match[0];
    let cls = "";
    if (token.startsWith("#")) cls = "tok-com";
    else if (token.startsWith("@")) cls = "tok-dec";
    else if (/^[bfru]{0,2}["']/.test(token) || token.startsWith('"""') || token.startsWith("'''")) cls = "tok-str";
    else if (/^\d/.test(token)) cls = "tok-num";
    else if (KEYWORDS.has(token)) cls = "tok-kw";
    else if (token === "self") cls = "tok-self";
    else if (BUILTINS.has(token)) cls = "tok-fn";
    else {
      const next = line.slice(match.index + token.length);
      if (/^\s*\(/.test(next)) cls = "tok-fn";
    }
    out += cls ? `<span class="${cls}">${escapeHtml(token)}</span>` : escapeHtml(token);
    last = match.index + token.length;
  }
  if (last < line.length) out += escapeHtml(line.slice(last));
  return out;
}

/** পুরো কোডকে হাইলাইট করা HTML লাইনের অ্যারেতে রূপান্তর করে */
export function highlightPython(code: string): string[] {
  const lines = code.split("\n");
  let inTriple = false;
  return lines.map((raw) => {
    const triples = (raw.match(/"""/g) ?? []).length;
    if (inTriple) {
      if (triples % 2 === 1) inTriple = false;
      return `<span class="tok-str">${escapeHtml(raw)}</span>`;
    }
    if (triples % 2 === 1) {
      inTriple = true;
      return `<span class="tok-str">${escapeHtml(raw)}</span>`;
    }
    return highlightSegment(raw);
  });
}

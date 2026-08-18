import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, extname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const htmlFiles = readdirSync(root).filter(name => extname(name) === ".html");
const errors = [];

const localTarget = (file, raw) => {
  if (/^(?:https?:|mailto:|tel:|data:|javascript:|#)/i.test(raw)) return null;
  const clean = decodeURIComponent(raw.split(/[?#]/, 1)[0]);
  return resolve(dirname(resolve(root, file)), clean);
};

for (const file of htmlFiles) {
  const html = readFileSync(resolve(root, file), "utf8");

  if (!/<title>[^<]+<\/title>/i.test(html)) errors.push(`${file}: missing title`);
  if (!/<main(?:\s|>)/i.test(html)) errors.push(`${file}: missing main landmark`);
  if (!/<\/html>\s*$/i.test(html)) errors.push(`${file}: missing closing html tag`);

  const ids = [...html.matchAll(/\sid=["']([^"']+)["']/gi)].map(match => match[1]);
  for (const id of new Set(ids)) {
    if (ids.filter(value => value === id).length > 1) errors.push(`${file}: duplicate id "${id}"`);
  }

  for (const match of html.matchAll(/<img\b[^>]*>/gi)) {
    if (!/\salt=["'][^"']*["']/i.test(match[0])) errors.push(`${file}: image missing alt text`);
  }

  for (const match of html.matchAll(/\s(?:href|src)=["']([^"']+)["']/gi)) {
    const target = localTarget(file, match[1]);
    if (!target) continue;
    if (!target.startsWith(root)) {
      errors.push(`${file}: local reference leaves repository: ${match[1]}`);
    } else if (!existsSync(target)) {
      errors.push(`${file}: missing local reference: ${relative(root, target)}`);
    }
  }
}

if (errors.length) {
  console.error(`Site validation failed with ${errors.length} issue(s):`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`Validated ${htmlFiles.length} HTML files: structure, image alternatives, IDs, and local links are present.`);

---
type: regex
pattern: '^(?=[\s\S]*viewbox)(?![\s\S]*<image)(?![\s\S]*data:image)[\s\S]*</svg>\s*$'
flags: i
target: { source: file, path: 'logo.svg' }
---

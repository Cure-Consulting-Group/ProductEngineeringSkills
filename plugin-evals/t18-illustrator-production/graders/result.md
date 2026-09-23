---
type: regex
pattern: '^(?=[\s\S]*DocumentColorMode\.CMYK)(?=[\s\S]*01_Primary)(?=[\s\S]*02_Stacked)(?=[\s\S]*03_Submark)(?=[\s\S]*04_Monochrome)(?=[\s\S]*Guides)(?=[\s\S]*Artwork)(?=[\s\S]*Typography)(?=[\s\S]*spots\.add)'
flags: i
target: { source: file, path: 'build_logo.jsx' }
---

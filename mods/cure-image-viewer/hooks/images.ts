import type { Pasted } from '../types'

/** A terminal cell is about twice as tall as it is wide. */
const CELL_ASPECT = 2
export const MAX_ROWS = 10
export const MAX_COLUMNS = 40
export const MAX_SHOWN = 4
/** The most an Image may carry inline, decoded: the element's own limit. */
export const MAX_INLINE_BYTES = 2 * 1024 * 1024

/** Whether the picture can be sent to the terminal as bytes. */
export function fitsInline(image: Pasted): boolean {
  return image.path !== null && image.path.endsWith('.png') && image.bytes > 0 && image.bytes <= MAX_INLINE_BYTES
}

/** The ids of every `[Image #N]` in a prompt, in order, each once. */
export function imageIds(text: string): number[] {
  const ids: number[] = []
  for (const m of text.matchAll(/\[Image #(\d+)\]/g)) {
    const id = Number(m[1])
    if (!ids.includes(id)) ids.push(id)
  }
  return ids
}

/** The folder name Claude Code derives from a working directory: every character outside A-Z a-z 0-9 becomes `-`. */
export function projectSlug(cwd: string): string {
  return cwd.replace(/[^a-zA-Z0-9]/g, '-')
}

/** Where this build saves a session's pasted images: `<tmp>/claude-<uid>/<slug>/<session>/images`, one candidate per tmp root. */
export function imageDirs(uid: string, cwd: string, sessionId: string): string[] {
  return ['/private/tmp', '/tmp'].map(tmp => `${tmp}/claude-${uid}/${projectSlug(cwd)}/${sessionId}/images`)
}

/** Reads `680 x 336` out of `file`'s line for a PNG; zeros when it is not there. */
export function parseSize(fileOutput: string): { width: number; height: number } {
  const m = /PNG image data, (\d+) x (\d+)/.exec(fileOutput)
  return m ? { width: Number(m[1]), height: Number(m[2]) } : { width: 0, height: 0 }
}

/** The box of cells a picture is drawn in: its own aspect, inside maxRows by `maxColumns`. */
export function cellBox(width: number, height: number, maxColumns: number = MAX_COLUMNS, maxRows: number = MAX_ROWS): { columns: number; rows: number } {
  if (width <= 0 || height <= 0) return { columns: Math.min(MAX_COLUMNS, maxColumns), rows: maxRows }
  const limit = Math.max(1, Math.min(MAX_COLUMNS, maxColumns))
  let rows = maxRows
  let columns = Math.round((rows * CELL_ASPECT * width) / height)
  if (columns > limit) {
    columns = limit
    rows = Math.max(1, Math.round((columns * height) / (width * CELL_ASPECT)))
  }
  return { columns: Math.max(1, columns), rows: Math.min(maxRows, rows) }
}

export function caption(image: Pasted): string {
  if (image.path === null) return `[Image #${image.id}] not found on disk`
  const size = image.width > 0 ? ` ${image.width}×${image.height}` : ''
  const tooLarge = image.bytes > MAX_INLINE_BYTES ? ` · ${(image.bytes / (1024 * 1024)).toFixed(1)} MB, too large to draw` : ''
  return `[Image #${image.id}]${size}${tooLarge}`
}

export function sameIds(a: readonly Pasted[], ids: readonly number[]): boolean {
  return a.length === ids.length && a.every((image, i) => image.id === ids[i])
}

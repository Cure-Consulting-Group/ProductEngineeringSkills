import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Pasted } from '../types'
import { MAX_ROWS, MAX_SHOWN, caption, cellBox, fitsInline, imageDirs, imageIds, parseSize, sameIds } from './images'

/**
 * cure-image-viewer: draws the images you sent above the prompt until the
 * turn that carried them ends. Claude Code saves a pasted image when the
 * prompt is submitted, not when it is pasted, so there is nothing to draw
 * while it is still a draft.
 *
 * The plugin API gives a pasted image's kind, never its bytes, so the mod
 * reads the copy Claude Code saves in the session's own temp folder (see
 * imageDirs). That layout is this build's, not a documented contract: when a
 * file is not where expected the row says so instead of drawing nothing.
 *
 * The picture is drawn by the terminal through the kitty graphics protocol.
 * Its bytes are sent inline, not as a file path for the terminal to open:
 * Warp (0.2026.09.30) draws inline bytes and ignores a path, and inline is
 * the form every kitty-protocol terminal accepts. An image over 2 MiB cannot
 * go inline and is captioned instead.
 *
 * Setting, as an environment variable:
 *   CURE_IMAGE_DIR  the folder to read `<N>.png` from, when the default is wrong
 */

const draft = atom({ plugin: 'cure-image-viewer', key: 'draft' } as const, [] as Pasted[])
const sent = atom({ plugin: 'cure-image-viewer', key: 'sent' } as const, [] as Pasted[])

let dirs: string[] | undefined
// Base64 of each picture by path. Kept out of $.state: megabytes that every state read would copy.
const pixels = new Map<string, string>()

export const register: Register = on => {
  on('prompt.edit', async ($, e, next) => {
    const box = await next(e)
    const ids = imageIds(box.text)
    if (!sameIds(await read($, draft), ids)) {
      const found = await locate($, ids)
      await update($, draft, () => found)
    }
    return box
  })

  on('prompt.submit', async ($, e, next) => {
    const ids = imageIds(e.text)
    const found = ids.length > 0 ? await locate($, ids) : []
    await update($, sent, () => found)
    await update($, draft, () => [])
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    await update($, sent, () => [])
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    // A draft's images are not on disk yet; show the ones that are, else the sent ones.
    const drafted = (await read($, draft)).filter(image => image.path !== null)
    const images = drafted.length > 0 ? drafted : await read($, sent)
    if (images.length === 0 || e.props.hasSurvey) return next(e)

    const table = $.ui.resolve(e)
    const { Box, Text } = table
    const isNarrow = e.props.bodyColumns < 100 && images.length > 1
    const shown = isNarrow ? images.slice(0, 1) : images.slice(0, MAX_SHOWN)
    const png = new Map<number, string>()
    if ('Image' in table) {
      for (const image of shown) {
        const data = fitsInline(image) ? await bytesOf($, image.path as string) : undefined
        if (data) png.set(image.id, data)
      }
    }
    const each = Math.floor((e.props.bodyColumns - (shown.length - 1) * 2) / shown.length)
    const maxRows = Math.min(MAX_ROWS, e.props.maxRows || MAX_ROWS)

    return (
      <Box flexDirection="column">
        <Box flexDirection="row" gap={2}>
          {shown.map(image => {
            const data = png.get(image.id)
            if (!('Image' in table) || data === undefined) return <Text dimColor>{caption(image)}</Text>
            const size = cellBox(image.width, image.height, each, maxRows)
            return (
              <Box flexDirection="column">
                <table.Image
                  key={`image-${image.id}`}
                  source={{ png: data }}
                  columns={size.columns}
                  rows={size.rows}
                  alt={caption(image)}
                />
                <Text dimColor>{caption(image)}</Text>
              </Box>
            )
          })}
        </Box>
        {images.length > shown.length ? (
          <Text dimColor>+{images.length - shown.length} more{isNarrow ? ` (${images.length} images pasted)` : ''}</Text>
        ) : null}
      </Box>
    )
  })
}

async function bytesOf($: EngineInterface, path: string): Promise<string | undefined> {
  const held = pixels.get(path)
  if (held !== undefined) return held
  try {
    const { base64 } = await $.fs.read(path, { as: 'bytes' })
    pixels.set(path, base64)
    return base64
  } catch {
    return undefined
  }
}

async function candidateDirs($: EngineInterface): Promise<string[]> {
  const override = await $.env.get('CURE_IMAGE_DIR')
  if (override) return [override]
  if (dirs) return dirs
  const uid = (await $.process.run(['id', '-u'])).stdout.trim()
  const id = await $.session.id()
  const roots = [...new Set([await $.session.cwd(), await $.session.root()])]
  dirs = roots.flatMap(cwd => imageDirs(uid, cwd, id))
  return dirs
}

async function locate($: EngineInterface, ids: readonly number[]): Promise<Pasted[]> {
  const folders = await candidateDirs($).catch(() => [] as string[])
  const out: Pasted[] = []
  for (const id of ids) {
    let path: string | null = null
    let bytes = 0
    for (const folder of folders) {
      const entries = await $.fs.list(folder).catch(() => [])
      const hit = entries.find(entry => entry.kind === 'file' && entry.name.startsWith(`${id}.`))
      if (hit) {
        path = `${folder}/${hit.name}`
        bytes = hit.size
        break
      }
    }
    const size = path ? parseSize((await $.process.run(['file', path]).catch(() => ({ stdout: '' }))).stdout) : { width: 0, height: 0 }
    out.push({ id, path, ...size, bytes })
  }
  return out
}

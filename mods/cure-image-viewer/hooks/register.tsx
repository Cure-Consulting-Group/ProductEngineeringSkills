import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Pasted } from '../types'
import { MAX_SHOWN, caption, cellBox, imageDirs, imageIds, parseSize, sameIds } from './images'

/**
 * cure-image-viewer: draws the images you paste above the prompt, from the
 * moment the draft names one (`[Image #1]`) until the turn that sent it ends.
 *
 * The plugin API gives a pasted image's kind, never its bytes, so the mod
 * reads the copy Claude Code saves in the session's own temp folder (see
 * imageDirs). That layout is this build's, not a documented contract: when a
 * file is not where expected the row says so instead of drawing nothing.
 *
 * The picture itself is drawn by the terminal (kitty graphics protocol:
 * kitty, Ghostty). Elsewhere the engine draws the caption in its place.
 *
 * Setting, as an environment variable:
 *   CURE_IMAGE_DIR  the folder to read `<N>.png` from, when the default is wrong
 */

const draft = atom({ plugin: 'cure-image-viewer', key: 'draft' } as const, [] as Pasted[])
const sent = atom({ plugin: 'cure-image-viewer', key: 'sent' } as const, [] as Pasted[])

let dirs: string[] | undefined

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
    const drafted = await read($, draft)
    const images = drafted.length > 0 ? drafted : await read($, sent)
    if (images.length === 0 || e.props.hasSurvey) return next(e)

    const table = $.ui.resolve(e)
    const { Box, Text } = table
    const shown = images.slice(0, MAX_SHOWN)
    const each = Math.floor((e.props.bodyColumns - (shown.length - 1) * 2) / shown.length)

    return (
      <Box flexDirection="column">
        <Box flexDirection="row" gap={2}>
          {shown.map(image => {
            const picture = 'Image' in table && image.path !== null && image.path.endsWith('.png')
            if (!picture) return <Text dimColor>{caption(image)}</Text>
            const size = cellBox(image.width, image.height, each)
            return (
              <Box flexDirection="column">
                <table.Image
                  key={`image-${image.id}`}
                  source={{ file: image.path as string, format: 'png' }}
                  columns={size.columns}
                  rows={size.rows}
                  alt={caption(image)}
                />
                <Text dimColor>{caption(image)}</Text>
              </Box>
            )
          })}
        </Box>
        {images.length > shown.length ? <Text dimColor>+{images.length - shown.length} more</Text> : null}
      </Box>
    )
  })
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
    for (const folder of folders) {
      const entries = await $.fs.list(folder).catch(() => [])
      const hit = entries.find(entry => entry.kind === 'file' && entry.name.startsWith(`${id}.`))
      if (hit) {
        path = `${folder}/${hit.name}`
        break
      }
    }
    const size = path ? parseSize((await $.process.run(['file', path]).catch(() => ({ stdout: '' }))).stdout) : { width: 0, height: 0 }
    out.push({ id, path, ...size })
  }
  return out
}

import { expect, mock, test } from 'claude-code/testing'

import { MAX_COLUMNS, MAX_INLINE_BYTES, MAX_ROWS, caption, cellBox, fitsInline, imageDirs, imageIds, parseSize, projectSlug, sameIds } from './images'

test('imageIds finds each pasted image once, in order', async () => {
  expect(imageIds('look at [Image #2] and [Image #1], then [Image #2] again')).toEqual([2, 1])
  expect(imageIds('no images, just [Image] and Image #3')).toEqual([])
})

test('the session image folder is derived as this build lays it out', async () => {
  expect(projectSlug('/Users/a.b/Documents/Cure-Consulting-Group/cure_finops')).toBe('-Users-a-b-Documents-Cure-Consulting-Group-cure-finops')
  expect(imageDirs('501', '/Users/me/repo', 'abc-123')).toEqual([
    '/private/tmp/claude-501/-Users-me-repo/abc-123/images',
    '/tmp/claude-501/-Users-me-repo/abc-123/images',
  ])
})

test('parseSize reads a PNG size from file(1) and gives zeros otherwise', async () => {
  expect(parseSize('/x/1.png: PNG image data, 680 x 336, 8-bit/color RGBA, non-interlaced')).toEqual({ width: 680, height: 336 })
  expect(parseSize('/x/1.jpg: JPEG image data')).toEqual({ width: 0, height: 0 })
})

test('cellBox keeps the picture\'s aspect inside the row and column limits', async () => {
  // 680x336 is about 2:1; at 10 rows that is 40 columns of half-width cells.
  expect(cellBox(680, 336)).toEqual({ columns: 40, rows: 10 })
  // A tall screenshot is limited by rows.
  expect(cellBox(400, 800)).toEqual({ columns: 10, rows: MAX_ROWS })
  // A wide banner is limited by columns and loses rows.
  expect(cellBox(2000, 200)).toEqual({ columns: MAX_COLUMNS, rows: 2 })
  // A narrow band narrows it further.
  expect(cellBox(680, 336, 20)).toEqual({ columns: 20, rows: 5 })
  // Unknown size: the largest box.
  expect(cellBox(0, 0)).toEqual({ columns: MAX_COLUMNS, rows: MAX_ROWS })
})

test('captions say when a file is missing', async () => {
  expect(caption({ id: 1, path: '/x/1.png', width: 680, height: 336, bytes: 40_000 })).toBe('[Image #1] 680×336')
  expect(caption({ id: 2, path: '/x/2.png', width: 0, height: 0, bytes: 0 })).toBe('[Image #2]')
  expect(caption({ id: 3, path: null, width: 0, height: 0, bytes: 0 })).toBe('[Image #3] not found on disk')
  expect(caption({ id: 4, path: '/x/4.png', width: 3024, height: 1964, bytes: 3 * 1024 * 1024 })).toBe('[Image #4] 3024×1964 · 3.0 MB, too large to draw')
})

test('only a PNG of known size within the inline limit is drawn', async () => {
  const image = { id: 1, path: '/x/1.png', width: 10, height: 10, bytes: MAX_INLINE_BYTES }
  expect(fitsInline(image)).toBe(true)
  expect(fitsInline({ ...image, bytes: MAX_INLINE_BYTES + 1 })).toBe(false)
  expect(fitsInline({ ...image, bytes: 0 })).toBe(false)
  expect(fitsInline({ ...image, path: '/x/1.jpg' })).toBe(false)
  expect(fitsInline({ ...image, path: null })).toBe(false)
})

test('sameIds compares what is shown with what the draft names', async () => {
  const shown = [{ id: 1, path: null, width: 0, height: 0, bytes: 0 }]
  expect(sameIds(shown, [1])).toBe(true)
  expect(sameIds(shown, [1, 2])).toBe(false)
  expect(sameIds([], [])).toBe(true)
})

// ── the hooks, end to end ──────────────────────────────────────────────────

const DIR = '/private/tmp/claude-501/-repo/sess-1/images'
const bandProps = { hasSurvey: false, isWorking: false, maxRows: 20, bodyColumns: 100, scroll: { offset: 0, bodyRows: 20 }, view: {} }

// A real 1x1 PNG: the engine refuses a source that is not one.
const PNG = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
const reads: string[] = []
const world = (on: any, files: string[], size = 40_000) => {
  reads.length = 0
  on('fs.read', (_$: unknown, e: any) => {
    reads.push(e.path ?? e)
    return { value: { base64: PNG } }
  })
  mock.env(on, {})
  on('session.id', () => ({ value: 'sess-1' }))
  on('session.cwd', () => ({ value: '/repo' }))
  on('session.root', () => ({ value: '/repo' }))
  on('fs.list', (_$: unknown, e: any) => ({ value: (e.path ?? e) === DIR ? files.map(name => ({ name, kind: 'file', size })) : [] }))
  on('process.run', (_$: unknown, e: any) => {
    const argv: string[] = e.argv ?? e
    if (argv[0] === 'id') return { value: { exitCode: 0, stdout: '501\n', stderr: '' } }
    return { value: { exitCode: 0, stdout: `${argv[1]}: PNG image data, 680 x 336, 8-bit/color RGBA`, stderr: '' } }
  })
  on('ui.render', ($$: any, e: any) => h($$.ui.resolve(e).Box, null) as never)
  on('prompt.submit', (_$: unknown, e: any) => ({ text: e.text }) as never)
  on('turn.complete', () => ({ text: '' }) as never)
}

test('a submitted image is drawn from the session folder until its turn ends', async ($, on) => {
  world(on, ['1.png'])
  const mount = () => $.ui.mount({ plugin: 'cure-image-viewer', surface: 'terminal', component: 'AbovePrompt', props: bandProps as never })

  expect(await (await mount()).findAll({ type: 'Image' })).toHaveLength(0)

  await $.prompt.submit({ text: 'what is this [Image #1]' } as never)
  const ui = await mount()
  const [image] = await ui.findAll({ type: 'Image' })
  // The bytes go inline: a terminal that will not open a path (Warp) still draws them.
  expect(image?.props).toMatchObject({ source: { png: PNG }, columns: 40, rows: 10, alt: '[Image #1] 680×336' })
  expect(reads).toEqual([`${DIR}/1.png`])

  await $.turn.complete({ turnId: 't1', reason: 'done' } as never)
  expect(await (await mount()).findAll({ type: 'Image' })).toHaveLength(0)
})

test('an image with no file on disk shows a caption saying so, not a blank', async ($, on) => {
  world(on, [])
  await $.prompt.submit({ text: '[Image #4]' } as never)
  const ui = await $.ui.mount({ plugin: 'cure-image-viewer', surface: 'terminal', component: 'AbovePrompt', props: bandProps as never })
  expect(await ui.findAll({ type: 'Image' })).toHaveLength(0)
  expect((await ui.findAll({ type: 'Text' })).map(el => el.text)).toEqual(['[Image #4] not found on disk'])
})

test('a surface with no Image element gets the caption', async ($, on) => {
  world(on, ['1.png'])
  await $.prompt.submit({ text: '[Image #1]' } as never)
  const ui = await $.ui.mount({ plugin: 'cure-image-viewer', surface: 'desktop', component: 'AbovePrompt', props: bandProps as never })
  expect((await ui.findAll({ type: 'Text' })).map(el => el.text)).toEqual(['[Image #1] 680×336'])
})

test('image 1 is not mistaken for image 10', async ($, on) => {
  world(on, ['10.png'])
  await $.prompt.submit({ text: '[Image #1]' } as never)
  const ui = await $.ui.mount({ plugin: 'cure-image-viewer', surface: 'terminal', component: 'AbovePrompt', props: bandProps as never })
  expect((await ui.findAll({ type: 'Text' })).map(el => el.text)).toEqual(['[Image #1] not found on disk'])
})

test('an image over the inline limit is captioned, not sent', async ($, on) => {
  world(on, ['1.png'], 3 * 1024 * 1024)
  await $.prompt.submit({ text: '[Image #1]' } as never)
  const ui = await $.ui.mount({ plugin: 'cure-image-viewer', surface: 'terminal', component: 'AbovePrompt', props: bandProps as never })
  expect(await ui.findAll({ type: 'Image' })).toHaveLength(0)
  expect((await ui.findAll({ type: 'Text' })).map(el => el.text)).toEqual(['[Image #1] 680×336 · 3.0 MB, too large to draw'])
  expect(reads).toEqual([])
})

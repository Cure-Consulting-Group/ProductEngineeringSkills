# Internal Critique and Quality Bar

Run before delivering any substantial work. Fix what fails; then deliver.

## Critique questions

**UX** Is the primary action obvious within two seconds? Is navigation predictable? Is anything unnecessary? Is important information buried below a fold or behind a gesture? Are interactions discoverable without a tutorial?

**Visual** Is the hierarchy strong in greyscale? Is typography doing the work, or are containers doing it? Is spacing intentional (one scale, no ad hoc values)? Is the composition balanced without being centred by default? Does it look generic; would a reader guess it was AI-generated?

**Platform** Does it feel native (navigation, controls, gestures, type)? Are safe areas, insets, and cutouts respected? Does it adapt across size classes with written rules?

**Accessibility** Can everyone use it: keyboard, screen reader, switch, large text, reduced motion? Contrast 4.5:1 text and 3:1 UI (`contrast_check.py` passes)? Touch targets 44 pt / 48 dp / 24 px minimum? Does the layout survive 200 percent text?

**Product** Does this make the task easier than before? Does it serve the stated business objective? What did it cost the user to get here?

**Brand** Is it recognisable? Is there one coherent design language across screens and platforms? Could another product easily look identical?

**Content** Was it tested with long, short, missing, zero, and many? Are empty and error states designed with a next step?

**States** Is the state matrix complete for every meaningful component and screen?

## Quality bar (all rows must hold)

| Dimension | Standard |
|---|---|
| Brand | distinctive and appropriate to the register |
| UX | understandable and efficient; ten questions answered |
| UI | visually sophisticated; hierarchy survives greyscale |
| Platform | native where appropriate; no skins |
| Responsive | intentional transformation rules per size class |
| Accessibility | WCAG 2.2 AA (web) or platform equivalents, designed in |
| System | tokens and components consistent and reusable; `tokens_lint.py` passes |
| Interaction | behaviour, scrolling, and motion defined |
| Assets | required production assets accounted for, with skipped ones named |
| Engineering | implementation cost understood; expensive items flagged with fallbacks |

## Definition of done

The deliverable includes: the ten-question answers (scaled to size), the decision record, the state matrix, the responsive rules, the review panel synthesis (for substantive work), the produced artefacts (not descriptions of them), and a limitations list naming what was not done and why.

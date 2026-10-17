# Day-plan HTML generation

For HTML versions of day plans under `plan/`, preserve the
look, feel, and behavior of `plan/week 1/2026-10-20_TUE.html`:

- Use the same mobile-first layout, color palette, typography, cards,
  timeline, checklist controls, bottom navigation, and responsive behavior.
- Keep the interactive timeline, live/preview controls, checklist persistence,
  expandable itinerary steps, and image viewer modal.
- Make every image in the viewer fully accessible on mobile. The image
  viewport must be a normal block scroll container with horizontal and
  vertical overflow. Keep oversized images in normal top-left flow; never
  center them with grid or flex alignment, because that can put their edges
  into inaccessible negative overflow. Reserve space below the fixed viewer
  bar so the top edge cannot be hidden or cropped.
- Reset both `scrollTop` and `scrollLeft` to zero whenever an image opens, so
  a previous image's scroll position cannot hide the new image's edges.
- Do not use `min-width` or `min-height` constraints that prevent zooming out.
  Provide image-specific zoom controls with a fit-width default, zoom-out,
  reset, and zoom-in behavior. The zoom-out control must reach at least 25%.
  Apply zoom by changing the image width so the scroll container includes the
  complete zoomed image; do not rely on browser page zoom or transforms that
  leave overflow dimensions incorrect.
- Reset zoom to 100% whenever a new image opens, and keep all zoom controls
  keyboard- and touch-accessible.
- Keep external web links as normal external links that open in a new tab.
- Keep CSS and JavaScript self-contained in the HTML unless explicitly
  requested otherwise.
- Preserve UTF-8 encoding when creating or editing HTML. Verify that visible
  symbols such as arrows, dashes, middots, currency signs, and expand/collapse
  icons render correctly; do not save HTML through a legacy Windows code page.
- Commit and push after every change.
- Whenever a day itinerary is added under `plan/`, add its HTML page to the day-by-day links in the root `index.html`.
- Whenever a step timing changes, update the timings of all subsequent steps.
- Warnings in step bodies must use the `.warning` visual style from the reference day plan.
- If no time is provided, ask the user; never guess or estimate unless explicitly asked.

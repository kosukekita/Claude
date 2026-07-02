# Motion & GSAP Patterns

Use this file when implementing, reviewing, or tuning UI animation with GSAP — hover micro-interactions, scroll reveals, staggered lists, page transitions, parallax, and loading states. Each pattern lists three intensity tiers (Subtle / Standard / Complex) with a copy-pasteable snippet, trigger, duration, easing, framework notes, do/don't rules, and performance notes. Pick the lowest tier that achieves the intent; escalate only when the design brief demands it.

## Hover Micro-interaction

### Subtle
- **Keywords:** hover, button, opacity, lift, press feedback
- **Trigger:** hover
- **Duration:** 150-200ms
- **Easing:** `power1.out`

```js
gsap.to(el, { y: -1, opacity: 0.9, duration: 0.15, ease: 'power1.out' });
```

- **Framework notes:** Bind on mouseenter/mouseleave; in React wrap in a ref + useEffect (or onMouseEnter/onMouseLeave props directly calling gsap.to).
- **Do:** Keep displacement under 2px so it reads as feedback not motion.
- **Don't:** Don't animate layout-affecting props (width/height/margin) on hover.
- **Performance:** Runs on transform/opacity only so it stays on the compositor thread.

### Standard
- **Keywords:** hover, card, scale, tilt, cursor feedback
- **Trigger:** hover
- **Duration:** 200-300ms
- **Easing:** `power2.out`

```js
gsap.to(el, { y: -4, scale: 1.02, boxShadow: '0 12px 24px rgba(0,0,0,0.12)', duration: 0.25, ease: 'power2.out' });
```

- **Framework notes:** Use `gsap.quickTo(el, 'y')` for cards with many hover targets to avoid re-creating tweens every event.
- **Do:** Pair with a matching mouseleave tween that reverses the same properties.
- **Don't:** Don't leave the hover state stuck if the pointer leaves fast; always attach the reverse tween.
- **Performance:** quickTo() avoids GC churn on lists with 20+ hoverable cards.

### Complex
- **Keywords:** hover, magnetic, cursor follow, 3d tilt
- **Trigger:** hover + mousemove
- **Duration:** 300-500ms
- **Easing:** `elastic.out(1,0.4)`

```js
const xTo = gsap.quickTo(el, 'x', { duration: 0.4, ease: 'elastic.out(1,0.4)' });
const yTo = gsap.quickTo(el, 'y', { duration: 0.4, ease: 'elastic.out(1,0.4)' });
el.addEventListener('mousemove', (e) => {
  const r = el.getBoundingClientRect();
  xTo((e.clientX - r.left - r.width/2) * 0.3);
  yTo((e.clientY - r.top - r.height/2) * 0.3);
});
```

- **Framework notes:** Debounce is not needed since quickTo interpolates; remove listeners on component unmount in React/Vue to avoid leaks.
- **Do:** Clamp the pull strength (e.g. `* 0.3`) so the element never fully leaves its hit box.
- **Don't:** Don't apply magnetic effect to more than 1-2 focal elements per screen; it becomes noisy.
- **Performance:** Use `will-change: transform` on the target element for smoother compositing.

## Scroll Reveal

### Subtle
- **Keywords:** scroll, fade in, reveal, on view
- **Trigger:** scroll (viewport enter)
- **Duration:** 300-400ms
- **Easing:** `power1.out`

```js
gsap.from(el, {
  opacity: 0, y: 12, duration: 0.35, ease: 'power1.out',
  scrollTrigger: { trigger: el, start: 'top 90%', toggleActions: 'play none none reverse' }
});
```

- **Framework notes:** Requires the ScrollTrigger plugin registered once via `gsap.registerPlugin(ScrollTrigger)`.
- **Do:** Keep the y offset small (8-16px) so it reads as a fade, not a slide.
- **Don't:** Don't reveal below-the-fold content needed for SEO/crawlers as invisible-by-default without a no-JS fallback.
- **Performance:** toggleActions `'play none none reverse'` avoids re-triggering on every scroll direction change.

### Standard
- **Keywords:** scroll, slide up, staggered section, reveal
- **Trigger:** scroll (viewport enter)
- **Duration:** 400-600ms
- **Easing:** `power2.out`

```js
gsap.from(el.children, {
  opacity: 0, y: 24, duration: 0.5, stagger: 0.08, ease: 'power2.out',
  scrollTrigger: { trigger: el, start: 'top 85%' }
});
```

- **Framework notes:** In React use `useGSAP(() => {...}, { scope: containerRef })` from @gsap/react to auto-cleanup on unmount.
- **Do:** Scope the ScrollTrigger to the section container so it doesn't re-scan the whole page.
- **Don't:** Don't stagger more than ~8 children; beyond that the last items feel laggy.
- **Performance:** Set scroller/markers: false in production; markers is dev-only.

### Complex
- **Keywords:** scroll, pin, scrub, storytelling, scrollytelling
- **Trigger:** scroll (continuous scrub)
- **Duration:** tied to scroll position
- **Easing:** none (scrub-driven)

```js
gsap.timeline({
  scrollTrigger: { trigger: section, start: 'top top', end: '+=150%', scrub: 1, pin: true }
})
  .from('.headline', { opacity: 0, y: 40 })
  .to('.bg-layer', { yPercent: -20 }, '<');
```

- **Framework notes:** Pinning needs the section to have deterministic height; recalc `ScrollTrigger.refresh()` after images/fonts load.
- **Do:** Use `scrub: true` or a small number (0.5-1.5) instead of instant jumps so it feels tied to the scrollbar.
- **Don't:** Don't pin more than 1-2 sections per page; excessive pinning fights native scroll feel and hurts mobile UX.
- **Performance:** Pinning forces layout reflow; test on mid-tier mobile devices, not just desktop.

## Stagger List

### Subtle
- **Keywords:** list, stagger, cards, grid entrance
- **Trigger:** load or scroll
- **Duration:** 250-350ms
- **Easing:** `power1.out`

```js
gsap.from('.list-item', { opacity: 0, y: 8, duration: 0.3, stagger: 0.03 });
```

- **Framework notes:** Select items with a stable class/data-attribute (not array index) so re-renders in React don't break targeting.
- **Do:** Keep per-item stagger delay small (0.02-0.04s) for lists longer than 10 items.
- **Don't:** Don't stagger by more than 0.1s per item on long lists; total reveal time becomes sluggish.
- **Performance:** For virtualized lists, only animate items currently mounted in the DOM.

### Standard
- **Keywords:** grid, bento, cards, staggered scale
- **Trigger:** load or scroll
- **Duration:** 300-450ms
- **Easing:** `back.out(1.4)`

```js
gsap.from('.grid-item', {
  opacity: 0, scale: 0.92, y: 16, duration: 0.4,
  stagger: { each: 0.06, from: 'start', grid: 'auto' },
  ease: 'back.out(1.4)'
});
```

- **Framework notes:** `grid: 'auto'` lets GSAP infer rows/columns from a CSS grid layout for a natural wave stagger.
- **Do:** Combine with `from: 'center'` for a bento-grid layout to draw the eye inward first.
- **Don't:** Don't use back.out on dense data tables; the overshoot reads as sloppy on informational UI.
- **Performance:** Group DOM writes; avoid interleaving layout reads (getBoundingClientRect) between staggered tweens.

### Complex
- **Keywords:** stagger, wave, text reveal, split text
- **Trigger:** load or scroll
- **Duration:** 400-700ms
- **Easing:** `expo.out`

```js
const split = new SplitText(headline, { type: 'chars' });
gsap.from(split.chars, { opacity: 0, y: 20, rotateX: -40, duration: 0.6, stagger: 0.015, ease: 'expo.out' });
```

- **Framework notes:** SplitText is a GSAP Club/paid plugin; confirm license before shipping and provide a plain fade fallback if unavailable.
- **Do:** Revert SplitText on unmount/cleanup (`split.revert()`) to restore original text nodes for accessibility tools.
- **Don't:** Don't split-animate long paragraphs; reserve for short headlines (under ~8 words).
- **Performance:** Splitting text creates one element per character; keep it to headline-length copy only for DOM size.

## Page Transition

### Subtle
- **Keywords:** route change, fade, page transition
- **Trigger:** route change
- **Duration:** 200-300ms
- **Easing:** `power1.inOut`

```js
gsap.to(main, {
  opacity: 0, duration: 0.2,
  onComplete: () => {
    navigate();
    gsap.fromTo(main, { opacity: 0 }, { opacity: 1, duration: 0.2 });
  }
});
```

- **Framework notes:** Pair with the router's transition hooks (Next.js App Router transitions, React Router's useNavigate, Vue Router's beforeEach/afterEach).
- **Do:** Preload the destination route's critical assets before the exit tween finishes.
- **Don't:** Don't block navigation on animation; cap exit duration at ~250ms so the app never feels unresponsive.
- **Performance:** Exit animation should always resolve faster than entrance (asymmetric timing) so back/forward feels snappy.

### Standard
- **Keywords:** route change, slide, overlay wipe
- **Trigger:** route change
- **Duration:** 400-600ms
- **Easing:** `power2.inOut`

```js
const tl = gsap.timeline();
tl.to('.transition-overlay', { yPercent: 0, duration: 0.4, ease: 'power2.inOut' })
  .call(navigate)
  .to('.transition-overlay', { yPercent: -100, duration: 0.4, ease: 'power2.inOut', delay: 0.1 });
```

- **Framework notes:** Keep the overlay element mounted at the layout root (outside the page component) so it survives the route swap.
- **Do:** Show a lightweight loading indicator if the destination route's data fetch outlasts the overlay.
- **Don't:** Don't tie the overlay's reveal directly to data-fetch completion without a max-wait timeout; a slow API stalls the whole transition.
- **Performance:** Prefer CSS transform (yPercent) over top/left to keep the overlay animation on the compositor thread.

### Complex
- **Keywords:** shared element, morph, hero transition
- **Trigger:** route change
- **Duration:** 500-800ms
- **Easing:** `expo.inOut`

```js
const state = Flip.getState('.hero-image');
navigate();
Flip.from(state, { duration: 0.6, ease: 'expo.inOut', absolute: true, zIndex: 100 });
```

- **Framework notes:** Requires the GSAP Flip plugin; the 'from' and 'to' route must render the same element with a shared `data-flip-id`.
- **Do:** Verify the shared element exists in both DOM states before calling Flip.from to avoid a silent no-op.
- **Don't:** Don't use shared-element transitions across more than one element pair per navigation; compounding Flips are hard to time correctly.
- **Performance:** Flip recalculates layout (FLIP technique) so test on low-end devices for jank.

## Parallax Scroll

### Subtle
- **Keywords:** parallax, background, depth, scroll speed
- **Trigger:** scroll (continuous)
- **Duration:** tied to scroll position
- **Easing:** linear (scrub)

```js
gsap.to('.bg-layer', { yPercent: 10, ease: 'none', scrollTrigger: { trigger: section, scrub: true } });
```

- **Framework notes:** Apply parallax to background/decorative layers only, never to text or interactive controls.
- **Do:** Keep the yPercent delta small (5-15) so foreground and background never desync distractingly.
- **Don't:** Don't parallax body copy; it hurts reading comfort and can trigger motion sickness.
- **Performance:** `will-change: transform` on the parallax layer only; remove it after scroll settles to free GPU memory.

### Standard
- **Keywords:** multi-layer parallax, depth, hero background
- **Trigger:** scroll (continuous)
- **Duration:** tied to scroll position
- **Easing:** linear (scrub)

```js
gsap.utils.toArray('.parallax-layer').forEach((layer, i) => {
  gsap.to(layer, {
    yPercent: (i + 1) * -8, ease: 'none',
    scrollTrigger: { trigger: layer.parentElement, scrub: 0.5 }
  });
});
```

- **Framework notes:** Layer count beyond 3-4 has diminishing visual return and multiplies scroll-listener cost.
- **Do:** Vary speed per layer (background slowest, foreground fastest) to sell the depth illusion.
- **Don't:** Don't let parallax layers overflow their container; clip with `overflow: hidden` on the wrapper.
- **Performance:** Batch all layers under one ScrollTrigger container where possible instead of one per layer.

## Loading / Skeleton

### Subtle
- **Keywords:** loading, skeleton, shimmer, pulse
- **Trigger:** on mount / async wait
- **Duration:** 1200-1600ms loop
- **Easing:** `sine.inOut`

```js
gsap.to('.skeleton', { backgroundPosition: '200% 0', duration: 1.4, ease: 'sine.inOut', repeat: -1 });
```

- **Framework notes:** Kill the loop tween (`tween.kill()`) as soon as real content mounts to avoid orphaned repeating animations.
- **Do:** Use a CSS gradient background-position sweep rather than opacity pulsing; reads as 'loading' more clearly.
- **Don't:** Don't run more than one shimmer loop per skeleton group; sync them under one timeline so the wave reads as a single unit.
- **Performance:** repeat: -1 tweens are cheap but must be explicitly killed on unmount or they leak in SPA route changes.

### Standard
- **Keywords:** progress, spinner, morphing loader
- **Trigger:** on mount / async wait
- **Duration:** 800-1200ms loop
- **Easing:** `power1.inOut`

```js
gsap.timeline({ repeat: -1 })
  .to('.loader-dot', { y: -8, duration: 0.4, stagger: { each: 0.15, yoyo: true, repeat: 1 } });
```

- **Framework notes:** Wrap the whole loop timeline in useGSAP with `{ revertOnUpdate: false }` in React so it isn't rebuilt every render.
- **Do:** Cap total loop duration under ~1.5s so long waits don't feel like the UI froze on a single beat.
- **Don't:** Don't use elaborate loaders for sub-300ms waits; they flash and feel worse than no indicator.
- **Performance:** Pause the timeline (`tl.pause()`) when the loading tab/view is not visible to save CPU on background tabs.

Source: ui-ux-pro-max motion.csv (MIT)

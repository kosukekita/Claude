# Code Patterns (Good vs Bad)

Use this file when writing or reviewing concrete UI/UX and React/Next.js code. Every entry keeps the exact Good and Bad code snippet pair from the source data, plus its Do/Don't guidance and severity, so you can copy the correct pattern and recognize the wrong one on sight. Snippets are preserved verbatim; they are illustrative shorthand, not always drop-in complete code. Organized by Category then Issue.

## UX Guidelines

### Navigation > Smooth Scroll

- Do: Use `scroll-behavior: smooth` on html element
- Don't: Jump directly without transition
- Severity: High

Good:
```css
html { scroll-behavior: smooth; }
```
Bad:
```html
<a href='#section'> without CSS
```

### Navigation > Sticky Navigation

- Do: Add padding-top to body equal to nav height
- Don't: Let nav overlap first section content
- Severity: Medium

Good:
```
pt-20 (if nav is h-20)
```
Bad:
```
No padding compensation
```

### Navigation > Active State

- Do: Highlight active nav item with color/underline
- Don't: No visual feedback on current location
- Severity: Medium

Good:
```
text-primary border-b-2
```
Bad:
```
All links same style
```

### Navigation > Back Button

- Do: Preserve navigation history properly
- Don't: Break browser/app back button behavior
- Severity: High

Good:
```js
history.pushState()
```
Bad:
```js
location.replace()
```

### Navigation > Deep Linking

- Do: Update URL on state/view changes
- Don't: Static URLs for dynamic content
- Severity: Medium

Good:
```
Use query params or hash
```
Bad:
```
Single URL for all states
```

### Navigation > Breadcrumbs

- Do: Use for sites with 3+ levels of depth
- Don't: Use for flat single-level sites
- Severity: Low

Good:
```
Home > Category > Product
```
Bad:
```
Only on deep nested pages
```

### Animation > Excessive Motion

- Do: Animate 1-2 key elements per view maximum
- Don't: Animate everything that moves
- Severity: High

Good:
```
Single hero animation
```
Bad:
```
animate-bounce on 5+ elements
```

### Animation > Duration Timing

- Do: Use 150-300ms for micro-interactions
- Don't: Use animations longer than 500ms for UI
- Severity: Medium

Good:
```
transition-all duration-200
```
Bad:
```
duration-1000
```

### Animation > Reduced Motion

- Do: Check prefers-reduced-motion media query
- Don't: Ignore accessibility motion settings
- Severity: High

Good:
```css
@media (prefers-reduced-motion: reduce)
```
Bad:
```
No motion query check
```

### Animation > Loading States

- Do: Use skeleton screens or spinners
- Don't: Leave UI frozen with no feedback
- Severity: High

Good:
```
animate-pulse skeleton
```
Bad:
```
Blank screen while loading
```

### Animation > Hover vs Tap

- Do: Use click/tap for primary interactions
- Don't: Rely only on hover for important actions
- Severity: High

Good:
```
onClick handler
```
Bad:
```
onMouseEnter only
```

### Animation > Continuous Animation

- Do: Use for loading indicators only
- Don't: Use for decorative elements
- Severity: Medium

Good:
```
animate-spin on loader
```
Bad:
```
animate-bounce on icons
```

### Animation > Transform Performance

- Do: Use transform and opacity for animations
- Don't: Animate width/height/top/left properties
- Severity: Medium

Good:
```css
transform: translateY()
```
Bad:
```css
top: 10px animation
```

### Animation > Easing Functions

- Do: Use ease-out for entering ease-in for exiting
- Don't: Use linear for UI transitions
- Severity: Low

Good:
```
ease-out
```
Bad:
```
linear
```

### Layout > Z-Index Management

- Do: Define z-index scale system (10 20 30 50)
- Don't: Use arbitrary large z-index values
- Severity: High

Good:
```
z-10 z-20 z-50
```
Bad:
```
z-[9999]
```

### Layout > Overflow Hidden

- Do: Test all content fits within containers
- Don't: Blindly apply overflow-hidden
- Severity: Medium

Good:
```
overflow-auto with scroll
```
Bad:
```
overflow-hidden truncating content
```

### Layout > Fixed Positioning

- Do: Account for safe areas and other fixed elements
- Don't: Stack multiple fixed elements carelessly
- Severity: Medium

Good:
```
Fixed nav + fixed bottom with gap
```
Bad:
```
Multiple overlapping fixed elements
```

### Layout > Stacking Context

- Do: Understand what creates new stacking context
- Don't: Expect z-index to work across contexts
- Severity: Medium

Good:
```
Parent with z-index isolates children
```
Bad:
```
z-index: 9999 not working
```

### Layout > Content Jumping

- Do: Reserve space for async content
- Don't: Let images/content push layout around
- Severity: High

Good:
```
aspect-ratio or fixed height
```
Bad:
```
No dimensions on images
```

### Layout > Viewport Units

- Do: Use dvh or account for mobile browser chrome
- Don't: Use 100vh for full-screen mobile layouts
- Severity: Medium

Good:
```
min-h-dvh or min-h-screen
```
Bad:
```
h-screen on mobile
```

### Layout > Container Width

- Do: Limit max-width for text content (65-75ch)
- Don't: Let text span full viewport width
- Severity: Medium

Good:
```
max-w-prose or max-w-3xl
```
Bad:
```
Full width paragraphs
```

### Touch > Touch Target Size

- Do: Minimum 44x44px touch targets
- Don't: Tiny clickable areas
- Severity: High

Good:
```
min-h-[44px] min-w-[44px]
```
Bad:
```
w-6 h-6 buttons
```

### Touch > Touch Spacing

- Do: Minimum 8px gap between touch targets
- Don't: Tightly packed clickable elements
- Severity: Medium

Good:
```
gap-2 between buttons
```
Bad:
```
gap-0 or gap-1
```

### Touch > Gesture Conflicts

- Do: Avoid horizontal swipe on main content
- Don't: Override system gestures
- Severity: Medium

Good:
```
Vertical scroll primary
```
Bad:
```
Horizontal swipe carousel only
```

### Touch > Tap Delay

- Do: Use touch-action CSS or fastclick
- Don't: Default mobile tap handling
- Severity: Medium

Good:
```css
touch-action: manipulation
```
Bad:
```
No touch optimization
```

### Touch > Pull to Refresh

- Do: Disable where not needed
- Don't: Enable by default everywhere
- Severity: Low

Good:
```css
overscroll-behavior: contain
```
Bad:
```
Default overscroll
```

### Touch > Haptic Feedback

- Do: Use for confirmations and important actions
- Don't: Overuse vibration feedback
- Severity: Low

Good:
```js
navigator.vibrate(10)
```
Bad:
```
Vibrate on every tap
```

### Interaction > Focus States

- Do: Use visible focus rings on interactive elements
- Don't: Remove focus outline without replacement
- Severity: High

Good:
```
focus:ring-2 focus:ring-blue-500
```
Bad:
```
outline-none without alternative
```

### Interaction > Hover States

- Do: Change cursor and add subtle visual change
- Don't: No hover feedback on clickable elements
- Severity: Medium

Good:
```
hover:bg-gray-100 cursor-pointer
```
Bad:
```
No hover style
```

### Interaction > Active States

- Do: Add pressed/active state visual change
- Don't: No feedback during interaction
- Severity: Medium

Good:
```
active:scale-95
```
Bad:
```
No active state
```

### Interaction > Disabled States

- Do: Reduce opacity and change cursor
- Don't: Confuse disabled with normal state
- Severity: Medium

Good:
```
opacity-50 cursor-not-allowed
```
Bad:
```
Same style as enabled
```

### Interaction > Loading Buttons

- Do: Disable button and show loading state
- Don't: Allow multiple clicks during processing
- Severity: High

Good:
```jsx
disabled={loading} spinner
```
Bad:
```
Button clickable while loading
```

### Interaction > Error Feedback

- Do: Show clear error messages near problem
- Don't: Silent failures with no feedback
- Severity: High

Good:
```
Red border + error message
```
Bad:
```
No indication of error
```

### Interaction > Success Feedback

- Do: Show success message or visual change
- Don't: No confirmation of completed action
- Severity: Medium

Good:
```
Toast notification or checkmark
```
Bad:
```
Action completes silently
```

### Interaction > Confirmation Dialogs

- Do: Confirm before delete/irreversible actions
- Don't: Delete without confirmation
- Severity: High

Good:
```
Are you sure modal
```
Bad:
```
Direct delete on click
```

### Accessibility > Color Contrast

- Do: Minimum 4.5:1 ratio for normal text
- Don't: Low contrast text
- Severity: High

Good:
```
#333 on white (7:1)
```
Bad:
```
#999 on white (2.8:1)
```

### Accessibility > Color Only

- Do: Use icons/text in addition to color
- Don't: Red/green only for error/success
- Severity: High

Good:
```
Red text + error icon
```
Bad:
```
Red border only for error
```

### Accessibility > Alt Text

- Do: Descriptive alt text for meaningful images
- Don't: Empty or missing alt attributes
- Severity: High

Good:
```html
alt='Dog playing in park'
```
Bad:
```html
alt='' for content images
```

### Accessibility > Heading Hierarchy

- Do: Use sequential heading levels h1-h6
- Don't: Skip heading levels or misuse for styling
- Severity: Medium

Good:
```
h1 then h2 then h3
```
Bad:
```
h1 then h4
```

### Accessibility > ARIA Labels

- Do: Add aria-label for icon-only buttons
- Don't: Icon buttons without labels
- Severity: High

Good:
```html
aria-label='Close menu'
```
Bad:
```jsx
<button><Icon/></button>
```

### Accessibility > Keyboard Navigation

- Do: Tab order matches visual order
- Don't: Keyboard traps or illogical tab order
- Severity: High

Good:
```jsx
tabIndex for custom order
```
Bad:
```
Unreachable elements
```

### Accessibility > Screen Reader

- Do: Use semantic HTML and ARIA properly
- Don't: Div soup with no semantics
- Severity: Medium

Good:
```html
<nav> <main> <article>
```
Bad:
```html
<div> for everything
```

### Accessibility > Form Labels

- Do: Use label with for attribute or wrap input
- Don't: Placeholder-only inputs
- Severity: High

Good:
```html
<label for='email'>
```
Bad:
```html
placeholder='Email' only
```

### Accessibility > Error Messages

- Do: Use aria-live or role=alert for errors
- Don't: Visual-only error indication
- Severity: High

Good:
```html
role='alert'
```
Bad:
```
Red border only
```

### Accessibility > Skip Links

- Do: Provide skip to main content link
- Don't: No skip link on nav-heavy pages
- Severity: Medium

Good:
```
Skip to main content link
```
Bad:
```
100 tabs to reach content
```

### Performance > Image Optimization

- Do: Use appropriate size and format (WebP)
- Don't: Unoptimized full-size images
- Severity: High

Good:
```html
srcset with multiple sizes
```
Bad:
```
4000px image for 400px display
```

### Performance > Lazy Loading

- Do: Lazy load below-fold images and content
- Don't: Load everything upfront
- Severity: Medium

Good:
```html
loading='lazy'
```
Bad:
```
All images eager load
```

### Performance > Code Splitting

- Do: Split code by route/feature
- Don't: Single large bundle
- Severity: Medium

Good:
```js
dynamic import()
```
Bad:
```
All code in main bundle
```

### Performance > Caching

- Do: Set appropriate cache headers
- Don't: No caching strategy
- Severity: Medium

Good:
```
Cache-Control headers
```
Bad:
```
Every request hits server
```

### Performance > Font Loading

- Do: Use font-display swap or optional
- Don't: Invisible text during font load
- Severity: Medium

Good:
```css
font-display: swap
```
Bad:
```
FOIT (Flash of Invisible Text)
```

### Performance > Third Party Scripts

- Do: Load non-critical scripts async/defer
- Don't: Synchronous third-party scripts
- Severity: Medium

Good:
```html
async or defer attribute
```
Bad:
```html
<script src='...'> in head
```

### Performance > Bundle Size

- Do: Monitor and minimize bundle size
- Don't: Ignore bundle size growth
- Severity: Medium

Good:
```
Bundle analyzer
```
Bad:
```
No size monitoring
```

### Performance > Render Blocking

- Do: Inline critical CSS defer non-critical
- Don't: Large blocking CSS files
- Severity: Medium

Good:
```
Critical CSS inline
```
Bad:
```
All CSS in head
```

### Forms > Input Labels

- Do: Always show label above or beside input
- Don't: Placeholder as only label
- Severity: High

Good:
```html
<label>Email</label><input>
```
Bad:
```html
placeholder='Email' only
```

### Forms > Error Placement

- Do: Show error below related input
- Don't: Single error message at top of form
- Severity: Medium

Good:
```
Error under each field
```
Bad:
```
All errors at form top
```

### Forms > Inline Validation

- Do: Validate on blur for most fields
- Don't: Validate only on submit
- Severity: Medium

Good:
```
onBlur validation
```
Bad:
```
Submit-only validation
```

### Forms > Input Types

- Do: Use email tel number url etc
- Don't: Text input for everything
- Severity: Medium

Good:
```html
type='email'
```
Bad:
```html
type='text' for email
```

### Forms > Autofill Support

- Do: Use autocomplete attribute properly
- Don't: Block or ignore autofill
- Severity: Medium

Good:
```html
autocomplete='email'
```
Bad:
```html
autocomplete='off' everywhere
```

### Forms > Required Indicators

- Do: Use asterisk or (required) text
- Don't: No indication of required fields
- Severity: Medium

Good:
```
* required indicator
```
Bad:
```
Guess which are required
```

### Forms > Password Visibility

- Do: Toggle to show/hide password
- Don't: No visibility toggle
- Severity: Medium

Good:
```
Show/hide password button
```
Bad:
```
Password always hidden
```

### Forms > Submit Feedback

- Do: Show loading then success/error state
- Don't: No feedback after submit
- Severity: High

Good:
```
Loading -> Success message
```
Bad:
```
Button click with no response
```

### Forms > Input Affordance

- Do: Use distinct input styling
- Don't: Inputs that look like plain text
- Severity: Medium

Good:
```
Border/background on inputs
```
Bad:
```
Borderless inputs
```

### Forms > Mobile Keyboards

- Do: Use inputmode attribute
- Don't: Default keyboard for all inputs
- Severity: Medium

Good:
```html
inputmode='numeric'
```
Bad:
```
Text keyboard for numbers
```

### Responsive > Mobile First

- Do: Start with mobile styles then add breakpoints
- Don't: Desktop-first causing mobile issues
- Severity: Medium

Good:
```
Default mobile + md: lg: xl:
```
Bad:
```
Desktop default + max-width queries
```

### Responsive > Breakpoint Testing

- Do: Test at 320 375 414 768 1024 1440
- Don't: Only test on your device
- Severity: Medium

Good:
```
Multiple device testing
```
Bad:
```
Single device development
```

### Responsive > Touch Friendly

- Do: Increase touch targets on mobile
- Don't: Same tiny buttons on mobile
- Severity: High

Good:
```
Larger buttons on mobile
```
Bad:
```
Desktop-sized targets on mobile
```

### Responsive > Readable Font Size

- Do: Minimum 16px body text on mobile
- Don't: Tiny text on mobile
- Severity: High

Good:
```
text-base or larger
```
Bad:
```
text-xs for body text
```

### Responsive > Viewport Meta

- Do: Use width=device-width initial-scale=1
- Don't: Missing or incorrect viewport
- Severity: High

Good:
```html
<meta name='viewport'...>
```
Bad:
```
No viewport meta tag
```

### Responsive > Horizontal Scroll

- Do: Ensure content fits viewport width
- Don't: Content wider than viewport
- Severity: High

Good:
```
max-w-full overflow-x-hidden
```
Bad:
```
Horizontal scrollbar on mobile
```

### Responsive > Image Scaling

- Do: Use max-width: 100% on images
- Don't: Fixed width images overflow
- Severity: Medium

Good:
```css
max-w-full h-auto
```
Bad:
```html
width='800' fixed
```

### Responsive > Table Handling

- Do: Use horizontal scroll or card layout
- Don't: Wide tables breaking layout
- Severity: Medium

Good:
```
overflow-x-auto wrapper
```
Bad:
```
Table overflows viewport
```

### Typography > Line Height

- Do: Use 1.5-1.75 for body text
- Don't: Cramped or excessive line height
- Severity: Medium

Good:
```
leading-relaxed (1.625)
```
Bad:
```
leading-none (1)
```

### Typography > Line Length

- Do: Limit to 65-75 characters per line
- Don't: Full-width text on large screens
- Severity: Medium

Good:
```
max-w-prose
```
Bad:
```
Full viewport width text
```

### Typography > Font Size Scale

- Do: Use consistent modular scale
- Don't: Random font sizes
- Severity: Medium

Good:
```
Type scale (12 14 16 18 24 32)
```
Bad:
```
Arbitrary sizes
```

### Typography > Font Loading

- Do: Reserve space with fallback font
- Don't: Layout shift when fonts load
- Severity: Medium

Good:
```css
font-display: swap + similar fallback
```
Bad:
```
No fallback font
```

### Typography > Contrast Readability

- Do: Use darker text on light backgrounds
- Don't: Gray text on gray background
- Severity: High

Good:
```
text-gray-900 on white
```
Bad:
```
text-gray-400 on gray-100
```

### Typography > Heading Clarity

- Do: Clear size/weight difference
- Don't: Headings similar to body text
- Severity: Medium

Good:
```
Bold + larger size
```
Bad:
```
Same size as body
```

### Feedback > Loading Indicators

- Do: Show spinner/skeleton for operations > 300ms
- Don't: No feedback during loading
- Severity: High

Good:
```
Skeleton or spinner
```
Bad:
```
Frozen UI
```

### Feedback > Empty States

- Do: Show helpful message and action
- Don't: Blank empty screens
- Severity: Medium

Good:
```
No items yet. Create one!
```
Bad:
```
Empty white space
```

### Feedback > Error Recovery

- Do: Provide clear next steps
- Don't: Error without recovery path
- Severity: Medium

Good:
```
Try again button + help link
```
Bad:
```
Error message only
```

### Feedback > Progress Indicators

- Do: Step indicators or progress bar
- Don't: No indication of progress
- Severity: Medium

Good:
```
Step 2 of 4 indicator
```
Bad:
```
No step information
```

### Feedback > Toast Notifications

- Do: Auto-dismiss after 3-5 seconds
- Don't: Toasts that never disappear
- Severity: Medium

Good:
```
Auto-dismiss toast
```
Bad:
```
Persistent toast
```

### Feedback > Confirmation Messages

- Do: Brief success message
- Don't: Silent success
- Severity: Medium

Good:
```
Saved successfully toast
```
Bad:
```
No confirmation
```

### Content > Truncation

- Do: Truncate with ellipsis and expand option
- Don't: Overflow or broken layout
- Severity: Medium

Good:
```
line-clamp-2 with expand
```
Bad:
```
Overflow or cut off
```

### Content > Date Formatting

- Do: Use relative or locale-aware dates
- Don't: Ambiguous date formats
- Severity: Low

Good:
```
2 hours ago or locale format
```
Bad:
```
01/02/03
```

### Content > Number Formatting

- Do: Use thousand separators or abbreviations
- Don't: Long unformatted numbers
- Severity: Low

Good:
```
1.2K or 1,234
```
Bad:
```
1234567
```

### Content > Placeholder Content

- Do: Use realistic sample data
- Don't: Lorem ipsum everywhere
- Severity: Low

Good:
```
Real sample content
```
Bad:
```
Lorem ipsum
```

### Onboarding > User Freedom

- Do: Provide Skip and Back buttons
- Don't: Force linear unskippable tour
- Severity: Medium

Good:
```
Skip Tutorial button
```
Bad:
```
Locked overlay until finished
```

### Search > Autocomplete

- Do: Show predictions as user types
- Don't: Require full type and enter
- Severity: Medium

Good:
```
Debounced fetch + dropdown
```
Bad:
```
No suggestions
```

### Search > No Results

- Do: Show 'No results' with suggestions
- Don't: Blank screen or '0 results'
- Severity: Medium

Good:
```
Try searching for X instead
```
Bad:
```
No results found.
```

### Data Entry > Bulk Actions

- Do: Allow multi-select and bulk edit
- Don't: Single row actions only
- Severity: Low

Good:
```
Checkbox column + Action bar
```
Bad:
```
Repeated actions per row
```

### AI Interaction > Disclaimer

- Do: Clearly label AI generated content
- Don't: Present AI as human
- Severity: High

Good:
```
AI Assistant label
```
Bad:
```
Fake human name without label
```

### AI Interaction > Streaming

- Do: Stream text response token by token
- Don't: Show loading spinner for 10s+
- Severity: Medium

Good:
```
Typewriter effect
```
Bad:
```
Spinner until 100% complete
```

### Spatial UI > Gaze Hover

- Platform: VisionOS
- Do: Scale/highlight element on look
- Don't: Static element until pinch
- Severity: High

Good:
```swift
hoverEffect()
```
Bad:
```
onTap only
```

### Spatial UI > Depth Layering

- Platform: VisionOS
- Do: Use glass material and z-offset
- Don't: Flat opaque panels blocking view
- Severity: Medium

Good:
```swift
.glassBackgroundEffect()
```
Bad:
```
bg-white
```

### Sustainability > Auto-Play Video

- Do: Click-to-play or pause when off-screen
- Don't: Auto-play high-res video loops
- Severity: Medium

Good:
```html
playsInline muted preload='none'
```
Bad:
```html
autoplay loop
```

### Sustainability > Asset Weight

- Do: Compress and lazy load 3D models
- Don't: Load 50MB textures
- Severity: Medium

Good:
```
Draco compression
```
Bad:
```
Raw .obj files
```

### AI Interaction > Feedback Loop

- Do: Thumps up/down or 'Regenerate'
- Don't: Static output only
- Severity: Low

Good:
```
Feedback component
```
Bad:
```
Read-only text
```

### Accessibility > Motion Sensitivity

- Do: Respect prefers-reduced-motion
- Don't: Force scroll effects
- Severity: High

Good:
```css
@media (prefers-reduced-motion)
```
Bad:
```js
ScrollTrigger.create()
```

## React Performance

### Async Waterfall > Defer Await

- Do: Move await operations into branches where they're needed
- Don't: Await at top of function blocking all branches
- Severity: Critical

Good:
```js
if (skip) return { skipped: true }; const data = await fetch()
```
Bad:
```js
const data = await fetch(); if (skip) return { skipped: true }
```

### Async Waterfall > Promise.all Parallel

- Do: Use Promise.all() for independent operations
- Don't: Sequential await for independent operations
- Severity: Critical

Good:
```js
const [user, posts] = await Promise.all([fetchUser(), fetchPosts()])
```
Bad:
```js
const user = await fetchUser(); const posts = await fetchPosts()
```

### Async Waterfall > Dependency Parallelization

- Do: Use better-all to start each task at earliest possible moment
- Don't: Wait for unrelated data before starting dependent fetch
- Severity: Critical

Good:
```js
await all({ user() {}, config() {}, profile() { return fetch((await this.$.user).id) } })
```
Bad:
```js
const [user, config] = await Promise.all([...]); const profile = await fetchProfile(user.id)
```

### Async Waterfall > API Route Optimization

- Do: Start promises early and await late
- Don't: Sequential awaits in API handlers
- Severity: Critical

Good:
```js
const sessionP = auth(); const configP = fetchConfig(); const session = await sessionP
```
Bad:
```js
const session = await auth(); const config = await fetchConfig()
```

### Async Waterfall > Suspense Boundaries

- Do: Wrap async components in Suspense boundaries
- Don't: Await data blocking entire page render
- Severity: High

Good:
```jsx
<Suspense fallback={<Skeleton />}><DataDisplay /></Suspense>
```
Bad:
```jsx
const data = await fetchData(); return <DataDisplay data={data} />
```

### Bundle Size > Barrel Imports

- Do: Import directly from source path
- Don't: Import from barrel/index files
- Severity: Critical

Good:
```js
import Check from 'lucide-react/dist/esm/icons/check'
```
Bad:
```js
import { Check } from 'lucide-react'
```

### Bundle Size > Dynamic Imports

- Do: Use dynamic() for heavy components
- Don't: Import heavy components at top level
- Severity: Critical

Good:
```js
const Monaco = dynamic(() => import('./monaco'), { ssr: false })
```
Bad:
```js
import { MonacoEditor } from './monaco-editor'
```

### Bundle Size > Defer Third Party

- Do: Load non-critical scripts after hydration
- Don't: Include analytics in main bundle
- Severity: Medium

Good:
```js
const Analytics = dynamic(() => import('@vercel/analytics'), { ssr: false })
```
Bad:
```js
import { Analytics } from '@vercel/analytics/react'
```

### Bundle Size > Conditional Loading

- Do: Dynamic import when feature enabled
- Don't: Import large modules unconditionally
- Severity: High

Good:
```js
useEffect(() => { if (enabled) import('./heavy.js') }, [enabled])
```
Bad:
```js
import { heavyData } from './heavy.js'
```

### Bundle Size > Preload Intent

- Do: Preload on user intent signals
- Don't: Load only on click
- Severity: Medium

Good:
```jsx
onMouseEnter={() => import('./editor')}
```
Bad:
```jsx
onClick={() => import('./editor')}
```

### Server > React.cache Dedup

- Do: Wrap data fetchers with cache()
- Don't: Fetch same data multiple times in tree
- Severity: Medium

Good:
```js
export const getUser = cache(async () => await db.user.find())
```
Bad:
```js
export async function getUser() { return await db.user.find() }
```

### Server > LRU Cache Cross-Request

- Do: Use LRU for cross-request caching
- Don't: Refetch same data on every request
- Severity: High

Good:
```js
const cache = new LRUCache({ max: 1000, ttl: 5*60*1000 })
```
Bad:
```js
Always fetch from database
```

### Server > Minimize Serialization

- Do: Pass only needed fields to client components
- Don't: Pass entire objects to client
- Severity: High

Good:
```jsx
<Profile name={user.name} />
```
Bad:
```jsx
<Profile user={user} /> // 50 fields serialized
```

### Server > Parallel Fetching

- Do: Use component composition for parallel fetches
- Don't: Sequential fetches in parent component
- Severity: Critical

Good:
```jsx
<Header /><Sidebar /> // both fetch in parallel
```
Bad:
```jsx
const header = await fetchHeader(); return <><div>{header}</div><Sidebar /></>
```

### Server > After Non-blocking

- Do: Use after() for logging/analytics
- Don't: Block response for non-critical operations
- Severity: Medium

Good:
```js
after(async () => { await logAction() }); return Response.json(data)
```
Bad:
```js
await logAction(); return Response.json(data)
```

### Client > SWR Deduplication

- Do: Use useSWR for client data fetching
- Don't: Manual fetch in useEffect
- Severity: Medium-High

Good:
```js
const { data } = useSWR('/api/users', fetcher)
```
Bad:
```js
useEffect(() => { fetch('/api/users').then(setUsers) }, [])
```

### Client > Event Listener Dedup

- Do: Use useSWRSubscription for shared listeners
- Don't: Register listener per component instance
- Severity: Low

Good:
```js
useSWRSubscription('global-keydown', () => { window.addEventListener... })
```
Bad:
```js
useEffect(() => { window.addEventListener('keydown', handler) }, [])
```

### Rerender > Defer State Reads

- Do: Read state on-demand in callbacks
- Don't: Subscribe to state used only in handlers
- Severity: Medium

Good:
```js
const handleClick = () => { const params = new URLSearchParams(location.search) }
```
Bad:
```js
const params = useSearchParams(); const handleClick = () => { params.get('ref') }
```

### Rerender > Memoized Components

- Do: Extract to memo() components
- Don't: Compute expensive values before early return
- Severity: Medium

Good:
```jsx
const UserAvatar = memo(({ user }) => ...); if (loading) return <Skeleton />
```
Bad:
```jsx
const avatar = useMemo(() => compute(user)); if (loading) return <Skeleton />
```

### Rerender > Narrow Dependencies

- Do: Use primitive values in dependency arrays
- Don't: Use object references as dependencies
- Severity: Low

Good:
```js
useEffect(() => { console.log(user.id) }, [user.id])
```
Bad:
```js
useEffect(() => { console.log(user.id) }, [user])
```

### Rerender > Derived State

- Do: Use derived boolean state
- Don't: Subscribe to continuous values
- Severity: Medium

Good:
```js
const isMobile = useMediaQuery('(max-width: 767px)')
```
Bad:
```js
const width = useWindowWidth(); const isMobile = width < 768
```

### Rerender > Functional setState

- Do: Use functional form: setState(curr => ...)
- Don't: Reference state directly in setState
- Severity: Medium

Good:
```js
setItems(curr => [...curr, newItem])
```
Bad:
```js
setItems([...items, newItem]) // items in deps
```

### Rerender > Lazy State Init

- Do: Use function form for expensive init
- Don't: Compute expensive value directly
- Severity: Medium

Good:
```js
useState(() => buildSearchIndex(items))
```
Bad:
```js
useState(buildSearchIndex(items)) // runs every render
```

### Rerender > Transitions

- Do: Use startTransition for non-urgent updates
- Don't: Block UI on every state change
- Severity: Medium

Good:
```js
startTransition(() => setScrollY(window.scrollY))
```
Bad:
```js
setScrollY(window.scrollY) // blocks on every scroll
```

### Rendering > SVG Animation Wrapper

- Do: Animate div wrapper around SVG
- Don't: Animate SVG element directly
- Severity: Low

Good:
```jsx
<div class='animate-spin'><svg>...</svg></div>
```
Bad:
```jsx
<svg class='animate-spin'>...</svg>
```

### Rendering > Content Visibility

- Do: Use content-visibility for long lists
- Don't: Render all list items immediately
- Severity: High

Good:
```css
.item { content-visibility: auto; contain-intrinsic-size: 0 80px }
```
Bad:
```
Render 1000 items without optimization
```

### Rendering > Hoist Static JSX

- Do: Hoist static elements to module scope
- Don't: Create static elements inside components
- Severity: Low

Good:
```jsx
const skeleton = <div class='animate-pulse' />; function C() { return skeleton }
```
Bad:
```jsx
function C() { return <div class='animate-pulse' /> }
```

### Rendering > Hydration No Flicker

- Do: Inject sync script for client-only values
- Don't: Use useEffect causing flash
- Severity: Medium

Good:
```jsx
<script dangerouslySetInnerHTML={{ __html: 'el.className = localStorage.theme' }} />
```
Bad:
```js
useEffect(() => setTheme(localStorage.theme), []) // flickers
```

### Rendering > Conditional Render

- Do: Use explicit ternary for conditionals
- Don't: Use && with potentially falsy numbers
- Severity: Low

Good:
```jsx
{count > 0 ? <Badge>{count}</Badge> : null}
```
Bad:
```jsx
{count && <Badge>{count}</Badge>} // renders '0'
```

### Rendering > Activity Component

- Do: Use Activity for expensive toggle components
- Don't: Unmount/remount on visibility toggle
- Severity: Medium

Good:
```jsx
<Activity mode={isOpen ? 'visible' : 'hidden'}><Menu /></Activity>
```
Bad:
```jsx
{isOpen && <Menu />} // loses state
```

### JS Perf > Batch DOM CSS

- Do: Use class toggle or cssText
- Don't: Change styles one property at a time
- Severity: Medium

Good:
```js
element.classList.add('highlighted')
```
Bad:
```js
el.style.width='100px'; el.style.height='200px'
```

### JS Perf > Index Map Lookup

- Do: Build index Map for O(1) lookups
- Don't: Use .find() in loops
- Severity: Low-Medium

Good:
```js
const byId = new Map(users.map(u => [u.id, u])); byId.get(id)
```
Bad:
```js
users.find(u => u.id === order.userId) // O(n) each time
```

### JS Perf > Cache Property Access

- Do: Cache values before loops
- Don't: Access nested properties in loops
- Severity: Low-Medium

Good:
```js
const val = obj.config.settings.value; for (...) process(val)
```
Bad:
```js
for (...) process(obj.config.settings.value)
```

### JS Perf > Cache Function Results

- Do: Use Map cache for repeated calls
- Don't: Recompute same values repeatedly
- Severity: Medium

Good:
```js
const cache = new Map(); if (cache.has(x)) return cache.get(x)
```
Bad:
```js
slugify(name) // called 100 times same input
```

### JS Perf > Cache Storage API

- Do: Cache storage reads in Map
- Don't: Read storage on every call
- Severity: Low-Medium

Good:
```js
if (!cache.has(key)) cache.set(key, localStorage.getItem(key))
```
Bad:
```js
localStorage.getItem('theme') // every call
```

### JS Perf > Combine Iterations

- Do: Single loop for multiple categorizations
- Don't: Chain multiple filter() calls
- Severity: Low-Medium

Good:
```js
for (u of users) { if (u.isAdmin) admins.push(u); if (u.isTester) testers.push(u) }
```
Bad:
```js
users.filter(admin); users.filter(tester); users.filter(inactive)
```

### JS Perf > Length Check First

- Do: Early return if lengths differ
- Don't: Always run expensive comparison
- Severity: Medium-High

Good:
```js
if (a.length !== b.length) return true; // then compare
```
Bad:
```js
a.sort().join() !== b.sort().join() // even when lengths differ
```

### JS Perf > Early Return

- Do: Return immediately on first error
- Don't: Process all items then check errors
- Severity: Low-Medium

Good:
```js
for (u of users) { if (!u.email) return { error: 'Email required' } }
```
Bad:
```js
let hasError; for (...) { if (!email) hasError=true }; if (hasError)...
```

### JS Perf > Hoist RegExp

- Do: Hoist RegExp to module scope
- Don't: Create RegExp every render
- Severity: Low-Medium

Good:
```js
const EMAIL_RE = /^[^@]+@[^@]+$/; function validate() { EMAIL_RE.test(x) }
```
Bad:
```js
function C() { const re = new RegExp(pattern); re.test(x) }
```

### JS Perf > Loop Min Max

- Do: Single pass loop for min/max
- Don't: Sort array to find min/max
- Severity: Low

Good:
```js
let max = arr[0]; for (x of arr) if (x > max) max = x
```
Bad:
```js
arr.sort((a,b) => b-a)[0] // O(n log n)
```

### JS Perf > Set Map Lookups

- Do: Convert to Set for membership checks
- Don't: Use .includes() for repeated checks
- Severity: Low-Medium

Good:
```js
const allowed = new Set(['a','b']); allowed.has(id)
```
Bad:
```js
const allowed = ['a','b']; allowed.includes(id)
```

### JS Perf > toSorted Immutable

- Do: Use toSorted() for immutability
- Don't: Mutate arrays with sort()
- Severity: Medium-High

Good:
```js
users.toSorted((a,b) => a.name.localeCompare(b.name))
```
Bad:
```js
users.sort((a,b) => a.name.localeCompare(b.name)) // mutates
```

### Advanced > Event Handler Refs

- Do: Use useEffectEvent for stable handlers
- Don't: Re-subscribe on every callback change
- Severity: Low

Good:
```js
const onEvent = useEffectEvent(handler); useEffect(() => { listen(onEvent) }, [])
```
Bad:
```js
useEffect(() => { listen(handler) }, [handler]) // re-subscribes
```

### Advanced > useLatest Hook

- Do: Use useLatest for fresh values in stable callbacks
- Don't: Add callback to effect dependencies
- Severity: Low

Good:
```js
const cbRef = useLatest(cb); useEffect(() => { setTimeout(() => cbRef.current()) }, [])
```
Bad:
```js
useEffect(() => { setTimeout(() => cb()) }, [cb]) // re-runs
```

Source: ui-ux-pro-max ux-guidelines.csv + react-performance.csv (MIT)
</content>
</invoke>

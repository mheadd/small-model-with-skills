# USWDS v3 — Targeted Reference for Common Patterns

Use these exact class names and HTML structures when generating U.S. Web Design System (USWDS) v3 markup.

## Critical: BEM Naming Convention

USWDS v3 uses strict BEM (Block Element Modifier) naming:
- **Block**: `usa-alert`
- **Element** (double underscore): `usa-alert__body`, `usa-alert__heading`
- **Modifier** (double dash): `usa-alert--info`, `usa-alert--warning`

Never use single dashes for modifiers (e.g., `usa-alert-info` is WRONG).

---

## Government Banner

The official government website banner is a distinct component from the site header.

```html
<section class="usa-banner" aria-label="Official website of the United States government">
  <div class="usa-accordion">
    <header class="usa-banner__header">
      <div class="usa-banner__inner">
        <div class="grid-col-auto">
          <img aria-hidden="true" class="usa-banner__header-flag" src="/assets/img/us_flag_small.png" alt="">
        </div>
        <div class="grid-col-fill tablet:grid-col-auto" aria-hidden="true">
          <p class="usa-banner__header-text">An official website of the United States government</p>
          <p class="usa-banner__header-action">Here's how you know</p>
        </div>
        <button type="button" class="usa-accordion__button usa-banner__button" aria-expanded="false" aria-controls="gov-banner-default">
          <span class="usa-banner__button-text">Here's how you know</span>
        </button>
      </div>
    </header>
    <div class="usa-banner__content usa-accordion__content" id="gov-banner-default">
      <div class="grid-row grid-gap-lg">
        <div class="usa-banner__guidance tablet:grid-col-6">
          <img class="usa-banner__icon usa-media-block__img" src="/assets/img/icon-dot-gov.svg" role="img" alt="" aria-hidden="true">
          <div class="usa-media-block__body">
            <p><strong>Official websites use .gov</strong><br>A <strong>.gov</strong> website belongs to an official government organization in the United States.</p>
          </div>
        </div>
        <div class="usa-banner__guidance tablet:grid-col-6">
          <img class="usa-banner__icon usa-media-block__img" src="/assets/img/icon-https.svg" role="img" alt="" aria-hidden="true">
          <div class="usa-media-block__body">
            <p><strong>Secure .gov websites use HTTPS</strong><br>A <strong>lock</strong> or <strong>https://</strong> means you've safely connected to the .gov website.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
```

Key classes: `usa-banner`, `usa-banner__header`, `usa-banner__content`, `usa-banner__inner`
Required element: `<section>` (not `<div>`)
Required attribute: `aria-label` on the `<section>`

---

## Alert Components

Each alert requires a wrapper `<div>` with the variant modifier, a `usa-alert__body` inner div, and heading/text elements.

```html
<div class="usa-alert usa-alert--info">
  <div class="usa-alert__body">
    <h3 class="usa-alert__heading">Informative status</h3>
    <p class="usa-alert__text">An info message for the user.</p>
  </div>
</div>

<div class="usa-alert usa-alert--success">
  <div class="usa-alert__body">
    <h3 class="usa-alert__heading">Success status</h3>
    <p class="usa-alert__text">A success message.</p>
  </div>
</div>

<div class="usa-alert usa-alert--warning">
  <div class="usa-alert__body">
    <h3 class="usa-alert__heading">Warning status</h3>
    <p class="usa-alert__text">A warning message.</p>
  </div>
</div>

<div class="usa-alert usa-alert--error">
  <div class="usa-alert__body">
    <h3 class="usa-alert__heading">Error status</h3>
    <p class="usa-alert__text">An error message.</p>
  </div>
</div>
```

Alert variant modifiers: `usa-alert--info`, `usa-alert--success`, `usa-alert--warning`, `usa-alert--error`
Required inner wrapper: `usa-alert__body`
Heading element: `<h3>` with class `usa-alert__heading`
Text element: `<p>` with class `usa-alert__text`

---

## Grid System (v3)

USWDS v3 uses a 12-column grid. Do NOT use old v1 classes like `usa-grid` or `usa-width-*`.

```html
<div class="grid-container">
  <div class="grid-row grid-gap">
    <div class="grid-col-12 tablet:grid-col-6 desktop:grid-col-3">
      <!-- Content -->
    </div>
    <div class="grid-col-12 tablet:grid-col-6 desktop:grid-col-3">
      <!-- Content -->
    </div>
  </div>
</div>
```

- Container: `grid-container`
- Row: `grid-row`
- Gutters: `grid-gap` (on the row)
- Columns: `grid-col`, `grid-col-1` through `grid-col-12`, `grid-col-auto`, `grid-col-fill`
- Responsive prefixes: `tablet:grid-col-6`, `desktop:grid-col-4`

Two-column sidebar layout (3/9 split):
```html
<div class="grid-container">
  <div class="grid-row grid-gap">
    <div class="grid-col-12 desktop:grid-col-3">
      <!-- Side navigation -->
    </div>
    <div class="grid-col-12 desktop:grid-col-9">
      <!-- Main content -->
    </div>
  </div>
</div>
```

---

## Card Group

Cards in a grid must be wrapped in a `usa-card-group` container, and each card needs a `usa-card__container` inner wrapper.

```html
<ul class="usa-card-group">
  <li class="usa-card grid-col-12 tablet:grid-col-6 desktop:grid-col-3">
    <div class="usa-card__container">
      <div class="usa-card__header">
        <h3 class="usa-card__heading">Card title</h3>
      </div>
      <div class="usa-card__body">
        <p>Card description text.</p>
      </div>
      <div class="usa-card__footer">
        <button class="usa-button">Action</button>
      </div>
    </div>
  </li>
</ul>
```

Key classes: `usa-card-group`, `usa-card`, `usa-card__container`, `usa-card__header`, `usa-card__heading`, `usa-card__body`, `usa-card__footer`

---

## Step Indicator

The step indicator shows progress through a multi-step process. It uses an ordered list of segments.

```html
<div class="usa-step-indicator" aria-label="progress">
  <ol class="usa-step-indicator__segments">
    <li class="usa-step-indicator__segment usa-step-indicator__segment--complete">
      <span class="usa-step-indicator__segment-label">Personal Info <span class="usa-sr-only">completed</span></span>
    </li>
    <li class="usa-step-indicator__segment usa-step-indicator__segment--current" aria-current="step">
      <span class="usa-step-indicator__segment-label">Address <span class="usa-sr-only">current</span></span>
    </li>
    <li class="usa-step-indicator__segment">
      <span class="usa-step-indicator__segment-label">Review <span class="usa-sr-only">not completed</span></span>
    </li>
    <li class="usa-step-indicator__segment">
      <span class="usa-step-indicator__segment-label">Confirm <span class="usa-sr-only">not completed</span></span>
    </li>
  </ol>
  <div class="usa-step-indicator__header">
    <h2 class="usa-step-indicator__heading">
      <span class="usa-step-indicator__heading-counter">
        <span class="usa-sr-only">Step</span>
        <span class="usa-step-indicator__current-step">2</span>
        <span class="usa-step-indicator__total-steps">of 4</span>
      </span>
      <span class="usa-step-indicator__heading-text">Address</span>
    </h2>
  </div>
</div>
```

Key classes: `usa-step-indicator`, `usa-step-indicator__segments`, `usa-step-indicator__segment`, `usa-step-indicator__segment--complete`, `usa-step-indicator__segment--current`
Required elements: `<ol>` for segments, `<li>` for each step
Required attribute: `aria-current="step"` on the current segment

---

## Site Header (Basic)

```html
<header class="usa-header usa-header--basic">
  <div class="usa-nav-container">
    <div class="usa-navbar">
      <div class="usa-logo">
        <em class="usa-logo__text">
          <a href="/" title="Home">Agency Name</a>
        </em>
      </div>
      <button type="button" class="usa-menu-btn">Menu</button>
    </div>
    <nav aria-label="Primary navigation" class="usa-nav">
      <ul class="usa-nav__primary usa-accordion">
        <li class="usa-nav__primary-item">
          <a href="#" class="usa-nav-link">Item 1</a>
        </li>
      </ul>
      <section aria-label="Search component">
        <form class="usa-search usa-search--small" role="search">
          <label class="usa-sr-only" for="search-field">Search</label>
          <input class="usa-input" id="search-field" type="search" name="search">
          <button class="usa-button" type="submit"><span class="usa-sr-only">Search</span></button>
        </form>
      </section>
    </nav>
  </div>
</header>
```

Key classes: `usa-header`, `usa-header--basic`, `usa-navbar`, `usa-logo`, `usa-nav`, `usa-nav__primary`, `usa-search`

---

## Side Navigation

```html
<nav aria-label="Side navigation">
  <ul class="usa-sidenav">
    <li class="usa-sidenav__item">
      <a href="#">Page 1</a>
    </li>
    <li class="usa-sidenav__item">
      <a href="#" class="usa-current" aria-current="page">Current page</a>
    </li>
    <li class="usa-sidenav__item">
      <a href="#">Page 3</a>
    </li>
  </ul>
</nav>
```

- Active/current link: add class `usa-current` to the `<a>` element
- Accessibility: add `aria-current="page"` to the current link
- Always wrap in `<nav>` with `aria-label`

---

## Data Table

```html
<table class="usa-table usa-table--bordered usa-table--striped">
  <thead>
    <tr>
      <th scope="col">Column 1</th>
      <th scope="col">Column 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Data 1</td>
      <td>Data 2</td>
    </tr>
  </tbody>
</table>
```

Table modifier classes: `usa-table--bordered`, `usa-table--striped`, `usa-table--borderless`, `usa-table--stacked`
Required accessibility: `scope="col"` on `<th>` elements in `<thead>`
Tag component in cells: `<span class="usa-tag">Tag text</span>`

---

## Accessibility Checklist

- `aria-label` on `<nav>`, `<section>`, search `<form>`, and banner `<section>`
- `aria-current="page"` on current navigation links
- `aria-current="step"` on current step indicator segment
- `scope="col"` on table header cells
- `role="search"` on search forms
- Screen reader text: `<span class="usa-sr-only">descriptive text</span>`

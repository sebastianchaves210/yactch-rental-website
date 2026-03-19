# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Miami Yacht Collective** — A static yacht rental lead-generation website.
Goal: Convert visitors into booking leads via Call or WhatsApp.
No build tools, no frameworks, no package manager. Pure HTML/CSS/JS served directly from files.

## Dev Server

```bash
python3 -m http.server 8000
# Open http://localhost:8000
```

## Business Context

- **Primary CTA**: Every "Book" button triggers a modal with two options:
  - Call: (787) 664-5040
  - WhatsApp: links to wa.me/17876645040
- **Conversion goal**: Drive phone/WhatsApp contact — that IS the booking flow.
- **No backend**: No forms, no database, no payment processing. Intentionally lead-gen only.
- **Domain**: `https://miamiyachtcollective.com`
- **Social**: Instagram at `https://www.instagram.com/miamiyachtcollective/`

---

## Current Phase: Polish & Perfect

The site redesign (migrated from a Webflow "YachtLux" template) is complete. We are now editing and perfecting the website — fixing visuals, tweaking layouts, improving content, and ensuring everything looks great before launch.

### Site Structure

| Page | File | Purpose |
|------|------|---------|
| Homepage | `index.html` | Hero, fleet grid (9 yachts), FAQ, CTA sections |
| Isabella 48' | `isabella.html` | Yacht detail page |
| Maxum 46' | `maxum.html` | Yacht detail page |
| Ferretti 75' | `ferretti.html` | Yacht detail page |
| 55' Azimut | `azimut.html` | Yacht detail page |
| 90' Acgua Alberti | `acgua-alberti.html` | Yacht detail page |
| 25' Yamaha 255XD | `yamaha-255xd.html` | Yacht detail page (heavy gallery) |
| 65' Azimut L'chaim | `azimut-lchaim.html` | Yacht detail page (heavy gallery) |
| 90' Deep Blue | `deep-blue.html` | Yacht detail page (heavy gallery) |
| 62' Anvera | `anvera.html` | Yacht detail page (heavy gallery) |
| Gallery | `gallery.html` | Photo grid with lightbox |
| Blog | `blog.html` | Blog listing page |
| Blog articles | `blog/*.html` | 5 blog posts (use `../` prefix for assets) |
| About | `about.html` | About page |
| Services | `services.html` | Services overview |
| Contact | `contact.html` | Contact page |
| Booking | `booking.html` | Booking page |

### SEO Rules

Do not change these without explicit instruction:
- `<title>` tags
- `<meta name="description">` content
- `<h1>`, `<h2>`, `<h3>` text
- Image `src` and `alt` attributes
- Internal link `href` values
- Canonical URLs

### Booking Modal — Required on Every Page

Every page MUST include the booking modal. This is the business's conversion mechanism.

- Any "Book Now" / "Charter Now" / CTA button must have the `data-modal` attribute
- Modal offers two options: Call (787) 664-5040 or WhatsApp (wa.me/17876645040)
- The modal markup and JS must be present on every single page

---

## Fleet Data (Reference)

| Yacht | File | Price | Guests |
|-------|------|-------|--------|
| Isabella 48' W/ Jetski | `isabella.html` | $1,100 | 13 |
| Maxum 46' | `maxum.html` | $899 | 10 |
| Ferretti 75' | `ferretti.html` | $1,890 | 20 |
| 55' Azimut | `azimut.html` | $1,400 | 15 |
| 90' Acgua Alberti | `acgua-alberti.html` | $2,500 | 30 |
| 25' Yamaha 255XD | `yamaha-255xd.html` | $TBD | 10 |
| 65' Azimut L'chaim | `azimut-lchaim.html` | TBD | 20 |
| 90' Deep Blue W/ Jacuzzi | `deep-blue.html` | $2,500 | 30 |
| 62' Anvera | `anvera.html` | $1,200 | 15 |

## Do NOT

- Add npm, webpack, or any build step
- Rename any HTML files
- Change any `<title>`, `<meta description>`, heading text, image alt, or link href
- Break the booking modal flow (Call + WhatsApp)
- Replace `.avif` or existing image references with different paths
- Modify `sitemap.xml`
- Add payment forms, login, or backend functionality
- Use Webflow's CMS URL structure (like `/yachts/slug`) — keep flat file structure


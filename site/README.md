# LiquidJelly Cloudflare website

Direction 02: IBM Plex Sans, navy and restrained blue. Original LiquidJelly logo retained. No headshots. Content uses we/our and distinguishes older development experience from current AI services.

## Deployment

The GitHub repository is `cuperman007/liquidjelly`. Only pushes to **cf-pages** deploy this application. The old **gh-pages** branch and its existing website are untouched. The application lives in `site/`; the workflow lives at the repository root in `.github/workflows/cloudflare.yml`.

Hosting uses **Cloudflare Pages**, **Pages Functions**, **D1** and **Turnstile**. GitHub Actions builds and uploads the Pages site on commits to `cf-pages`; the Pages production branch is also `cf-pages`. Planned project: `liquidjelly-website`, with its actual `pages.dev` address returned by Cloudflare during provisioning. No custom-domain or DNS changes are part of this deployment.

Add the repository Actions secret `CLOUDFLARE_API_TOKEN`, scoped to Cloudflare account `f44a9a37fae8f8c1f4161be73b6289ce`, with Account permissions **Cloudflare Pages: Edit**, **D1: Edit**, **Turnstile: Edit**. The secret must be entered through GitHub settings, never committed. Account ID is non-secret and set in the workflow.

On each qualifying push, CI installs locked dependencies, builds the site, generates types, type-checks, tests the enquiry handler with a real local D1 database, and compiles the Pages Functions bundle. The deploy job reuses or creates the Pages project, the dedicated EU-restricted `liquidjelly-enquiries` database and `LiquidJelly enquiries` Turnstile widget, configures the production D1 binding and encrypted Turnstile secret, applies migrations, uploads the Pages deployment, then checks the public homepage, contact page, form configuration and rejection of an invalid submission. The Turnstile secret is masked in CI and sent directly to the Pages settings API; it is never written to source files. No real visitor data is used by smoke tests.

For the first push, a missing token produces a clear deployment failure; verification still runs. After adding the token, rerun the failed job from Actions. Manual workflow dispatch is available on cf-pages once GitHub discovers the workflow.

## Form and data

`POST /api/enquiries` validates and bounds input, rejects other origins and honeypot entries, validates Turnstile server-side including action and hostname, and uses a parameterised SQL insert. It does not expose a public list of enquiries. Success appears only after persistence. No personal details or Turnstile tokens are logged by application code. No email notification is sent automatically; authorised account administrators can read enquiries in the Cloudflare D1 dashboard. The form uses the existing public email address as a fallback.

Pages has no Cron Triggers. A D1 trigger removes enquiries older than 12 months whenever a new enquiry is saved. Administrators should also review/remove expired records during inactive periods; there is no scheduled deletion guarantee. The former standalone Worker scheduled handler has been removed. Privacy copy explains purpose, providers, retention and contact rights. D1 is restricted to the EU; this is not a claim that all Cloudflare edge processing is UK-only or EU-only. Review the business privacy notice before custom-domain launch.

## Local work

From `site/`:

```
npm ci
npm run build
npm run types
npm run check
npm test
npm run pages:build
npx wrangler d1 migrations apply DB --local
npm run dev
```

The zero UUID and empty public site key in the committed config are local placeholders. The deployment script resolves real resources without committing their secrets. Local form submission fails closed until test Turnstile settings are supplied using ignored `.dev.vars`; use Cloudflare's documented testing keys and a test hostname. Never configure test keys in production.

`build.py` generates the homepage, separate contact form, privacy page, sector page and seven case studies from `content/case-studies.md`. CSS, client JavaScript and local assets are in `dist/`. The Python static preview on port 8765 shows the design but cannot accept enquiries; use `npm run dev` (Pages local development) to test the backend. The form routes are in `functions/api/[[path]].js`; `dist/_routes.json` invokes Functions only for `/api/*`, keeping static page and asset requests out of the Functions allowance.

## Cost and service limits

Designed for Cloudflare's Free plan; no paid products or upgrade are required. Static asset delivery is free. Pages Functions share the Workers Free allowance of 100,000 dynamic requests/day; D1 Free includes 5 million rows read/day, 100,000 rows written/day and 5 GB storage across the account. Turnstile has a Free plan. Free limits are shared with other applications; exceeding them can interrupt the form. Existing paid-account billing settings are not changed by this project. GitHub Actions is free for standard hosted runners in this public repository.

Sources checked 29 September 2026:
- https://developers.cloudflare.com/pages/functions/pricing/
- https://developers.cloudflare.com/workers/platform/pricing/
- https://developers.cloudflare.com/d1/platform/pricing/
- https://developers.cloudflare.com/d1/configuration/data-location/
- https://developers.cloudflare.com/turnstile/plans/
- https://developers.cloudflare.com/turnstile/get-started/server-side-validation/

Brand sources are in ASSET-SOURCES.md. Relationship descriptions distinguish contract work, employed experience and customer platforms. One continuous scrolling row includes all companies across the seven sectors; reduced-motion preferences show static lists. Subsection numbers use the 01 / 01 format. Duplicate cards are hidden from assistive technology and keyboard focus. CV employers and customer brands are included with relationship labels; names without a matching logo use plain type. Historical company dates and claims have not been extended beyond the available source material. Pages remain noindex while under review.

Featured experience headlines include greyscale PHOENIX and UK Mail logos. Headline/logo opacity and position follow scroll position in both directions; keyboard focus reveals the title and reduced-motion preferences keep it static. UK Mail artwork attribution is published on credits.html.

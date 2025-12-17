# EhkoForge.ai Website - Quick Reference

*Action-oriented guide for deployment - December 17, 2025*
*Moved from CareerForge vault - December 17, 2025*

## Status

✅ **Complete and ready to deploy**
- All pages built (7 pages)
- All components created (13 components)
- Design system finalized
- Content written (2 blog posts production-ready)
- Deployment config ready
- Documentation framework established

**Priority:** After EhkoLabs site (professional presence first)

---

## Deployment Steps

### 1. Prepare Cloudflare (15 minutes)

1. Create free Cloudflare account at https://dash.cloudflare.com/sign-up
2. Note your Account ID (visible in URL after login)
3. Transfer ehkoforge.ai and ehkoforge.com to Cloudflare DNS

### 2. Create GitHub Repository (5 minutes)

1. Create new repository: `ehkoforge-website`
2. Clone locally
3. Copy all website files into repository
4. Commit and push

### 3. Connect Cloudflare Pages (10 minutes)

1. Workers & Pages → Create application → Pages
2. Connect to Git → Select `ehkoforge-website` repo
3. Configure build:
   - Framework preset: **Astro**
   - Build command: `npm run build`
   - Build output: `dist`
   - Node version: **20**
4. Click **Save and Deploy**

### 4. Configure Custom Domains (10 minutes)

1. Pages project → Custom domains → Set up a custom domain
2. Add: `ehkoforge.ai`, `www.ehkoforge.ai`, `ehkoforge.com`, `www.ehkoforge.com`
3. Wait ~5 minutes for SSL certificate provisioning

### 5. Set Up GitHub Actions (5 minutes)

Add secrets to GitHub:
- `CLOUDFLARE_API_TOKEN` (from Cloudflare API Tokens)
- `CLOUDFLARE_ACCOUNT_ID` (from dashboard URL)

### 6. Verify Everything (10 minutes)

Test all URLs and redirects, run Lighthouse audit (target >95).

---

## Quick Commands

```bash
# Local development
npm install
npm run dev

# Build and test
npm run build
npm run preview

# Deploy manually
npm run build
npx wrangler pages deploy ./dist --project-name=ehkoforge-ai
```

---

## File Structure

```
ehkoforge-website/
├── src/
│   ├── pages/ (7 pages)
│   ├── components/ (13 components)
│   ├── layouts/ (3 layouts)
│   └── styles/ (MDV design system)
├── public/
│   ├── _redirects
│   ├── _headers
│   └── images/
├── .github/workflows/deploy.yml
├── astro.config.mjs
├── wrangler.toml
└── package.json
```

---

## Resources

- **Cloudflare Pages:** https://developers.cloudflare.com/pages/
- **Astro Docs:** https://docs.astro.build/
- **Astro on Cloudflare:** https://docs.astro.build/en/guides/deploy/cloudflare/

---

**Total deployment time: ~1 hour**
**Ongoing maintenance: ~2 hours/month**

# Target LB Netlify lead gateway

This independent Netlify project proxies the **existing** Cloudflare Worker. It does not store Telegram tokens.

## Deployment

1. In Netlify, import GitHub repo `VAdym9083/gpt`.
2. Set **Branch** to `netlify-leads` (do NOT select `main`).
3. Set **Base directory** to `netlify-leads`.
4. The `netlify.toml` inside that directory configures `public` and `netlify/functions`. No build command is required.
5. Deploy. Open your Netlify-generated `https://*.netlify.app` URL on mobile and press the health-check button.
6. Only after verifying a real POST on mobile, update the main site's lead form endpoint to `https://YOUR-SITE.netlify.app/.netlify/functions/lead`.

`GET /.netlify/functions/lead` returns `{"status":"ready"}` and does not send leads.
`POST /.netlify/functions/lead` accepts form JSON and forwards to the existing Cloudflare Worker. It returns `{"success":true}` only after upstream confirmation.

Expected origin: `https://vadym9083.github.io`. Netlify's own origin is allowed for same-site tests.
Telegram secrets are not needed because the old Worker still delivers to Telegram.

**Do not point production at this endpoint until Netlify deployment and the Android test succeed.**

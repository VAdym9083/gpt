// Backend gateway between the GitHub Pages lead form and the existing
// Cloudflare Worker. Telegram credentials stay in Cloudflare, NOT GitHub.
// Netlify does not need TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID.
const SITE_ORIGIN = 'https://vadym9083.github.io';
const UPSTREAM_URL = 'https://target-lb-leads.vadym9083.workers.dev/';

function allowOrigin(origin) {
  if (origin === SITE_ORIGIN) return true;
  try {
    return !!origin && !!process.env.URL && origin === new URL(process.env.URL).origin;
  } catch {
    return false;
  }
}
function headers(origin) {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Cache-Control': 'no-store, max-age=0',
    'Vary': 'Origin'
  };
}
function json(statusCode, body, origin) {
  return { statusCode, headers: { 'Content-Type': 'application/json; charset=utf-8', ...headers(origin) },
    body: JSON.stringify(body) };
}
exports.handler = async (event) => {
  const method = event.httpMethod || 'GET';
  const origin = event.headers?.origin || event.headers?.Origin || '';
  // Health check is safe and sends no Telegram message.
  if (method === 'GET') {
    return json(200, { status: 'ready', service: 'target-lb-leads-gateway' }, origin === SITE_ORIGIN || allowOrigin(origin) ? origin : SITE_ORIGIN);
  }
  if (!allowOrigin(origin)) {
    return json(403, { success: false, error: 'Origin not allowed' }, SITE_ORIGIN);
  }
  if (method === 'OPTIONS') return { statusCode: 204, headers: headers(origin), body: '' };
  if (method !== 'POST') return json(405, { success: false, error: 'Method not allowed' }, origin);
  try {
    const raw = event.isBase64Encoded ? Buffer.from(event.body || '', 'base64').toString('utf8') : (event.body || '');
    if (raw.length > 5000) return json(413, { success: false, error: 'Payload too large' }, origin);
    let submitted;
    try { submitted = JSON.parse(raw); } catch { return json(400, { success: false, error: 'Invalid JSON' }, origin); }
    if (!submitted || typeof submitted !== 'object' || Array.isArray(submitted)) {
      return json(400, { success: false, error: 'Invalid request' }, origin);
    }
    const name = typeof submitted.name === 'string' ? submitted.name.trim() : '';
    const contact = typeof submitted.contact === 'string' ? submitted.contact.trim() : '';
    const network = submitted.network;
    if (name.length < 2 || name.length > 80 || contact.length < 3 || contact.length > 160 ||
        !['telegram', 'instagram', 'whatsapp'].includes(network)) {
      return json(422, { success: false, error: 'Invalid name, contact or messenger' }, origin);
    }
    // Keep page and UTM context; do not log personal contact details.
    const payload = {
      name, contact, network,
      lang: typeof submitted.lang === 'string' ? submitted.lang.slice(0, 10) : 'uk',
      page: typeof submitted.page === 'string' ? submitted.page.slice(0, 1000) : '',
      utm_source: typeof submitted.utm_source === 'string' ? submitted.utm_source.slice(0, 150) : '',
      utm_medium: typeof submitted.utm_medium === 'string' ? submitted.utm_medium.slice(0, 150) : '',
      utm_campaign: typeof submitted.utm_campaign === 'string' ? submitted.utm_campaign.slice(0, 150) : '',
      utm_content: typeof submitted.utm_content === 'string' ? submitted.utm_content.slice(0, 150) : '',
      utm_term: typeof submitted.utm_term === 'string' ? submitted.utm_term.slice(0, 150) : ''
    };
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch(UPSTREAM_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'text/plain;charset=UTF-8',
          'Origin': SITE_ORIGIN
        },
        body: JSON.stringify(payload),
        signal: controller.signal
      });
      const result = await response.json().catch(() => null);
      if (!response.ok || !result || result.success !== true) {
        // Do not claim a successful lead without Worker confirmation.
        return json(502, { success: false, error: 'Lead service did not confirm receipt' }, origin);
      }
      return json(200, { success: true }, origin);
    } finally {
      clearTimeout(timer);
    }
  } catch (error) {
    console.error('Gateway request failed:', error?.name || 'Error');
    return json(502, { success: false, error: 'Lead service unreachable' }, origin);
  }
};

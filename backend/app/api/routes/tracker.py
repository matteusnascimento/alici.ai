from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.tracker import WebsiteEventCreate, WebsiteEventRead
from app.services.website_tracker_service import WebsiteTrackerService

router = APIRouter(prefix="/tracker", tags=["tracker"])


@router.post("/events", response_model=WebsiteEventRead)
def record_website_event(payload: WebsiteEventCreate, db: Session = Depends(get_db)) -> WebsiteEventRead:
    return WebsiteTrackerService(db).record_event(payload)


@router.get("/script.js")
def tracker_script(site_id: str | None = None) -> Response:
    configured_site = site_id or "default"
    script = f"""
(function() {{
  var endpoint = (window.AXI_TRACKER_ENDPOINT || '/api/tracker/events');
  var siteId = {configured_site!r};
  var sessionKey = 'axi_tracker_session_id';
  var sessionId = localStorage.getItem(sessionKey);
  if (!sessionId) {{
    sessionId = 'axi-' + Math.random().toString(36).slice(2) + '-' + Date.now();
    localStorage.setItem(sessionKey, sessionId);
  }}
  var startedAt = Date.now();
  var pagesVisited = Number(sessionStorage.getItem('axi_tracker_pages') || '0') + 1;
  sessionStorage.setItem('axi_tracker_pages', String(pagesVisited));
  function params() {{
    var search = new URLSearchParams(window.location.search);
    return {{
      site_id: siteId,
      session_id: sessionId,
      page_url: window.location.href,
      referrer: document.referrer || null,
      traffic_source: search.get('utm_source') || document.referrer || 'direct',
      device: /Mobi|Android/i.test(navigator.userAgent) ? 'mobile' : 'desktop',
      utm_source: search.get('utm_source'),
      utm_medium: search.get('utm_medium'),
      utm_campaign: search.get('utm_campaign'),
      pages_visited: pagesVisited
    }};
  }}
  function send(eventType, extra) {{
    var body = Object.assign(params(), extra || {{}}, {{ event_type: eventType }});
    try {{
      navigator.sendBeacon(endpoint, new Blob([JSON.stringify(body)], {{ type: 'application/json' }}));
    }} catch (err) {{
      fetch(endpoint, {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify(body), keepalive: true }});
    }}
  }}
  send('page_view');
  document.addEventListener('click', function(event) {{
    var target = event.target && event.target.closest ? event.target.closest('a,button,[data-axi-track]') : null;
    if (target) send('click', {{ click_target: target.getAttribute('data-axi-track') || target.textContent || target.href || null }});
  }}, true);
  window.addEventListener('beforeunload', function() {{
    send('duration', {{ duration_seconds: Math.round((Date.now() - startedAt) / 1000) }});
  }});
  window.AXITracker = {{
    quote: function(value, metadata) {{ send('quote', {{ quote_value: value || null, metadata: metadata || {{}} }}); }},
    reservation: function(value, metadata) {{ send('reservation', {{ reservation_value: value || null, metadata: metadata || {{}} }}); }},
    search: function(metadata) {{ send('search', {{ metadata: metadata || {{}} }}); }}
  }};
}})();
"""
    return Response(content=script.strip(), media_type="application/javascript")

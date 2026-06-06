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
  var currentScript = document.currentScript || (function() {{
    var scripts = document.getElementsByTagName('script');
    return scripts[scripts.length - 1];
  }})();
  var endpoint = (
    (currentScript && currentScript.getAttribute('data-axi-endpoint')) ||
    window.AXI_TRACKER_ENDPOINT ||
    '/api/tracker/events'
  );
  var siteId = (currentScript && currentScript.getAttribute('data-axi-company-id')) || {configured_site!r};
  var visitorKey = 'axi_tracker_visitor_id';
  var visitorId = localStorage.getItem(visitorKey);
  if (!visitorId) {{
    visitorId = 'axiv-' + Math.random().toString(36).slice(2) + '-' + Date.now();
    localStorage.setItem(visitorKey, visitorId);
  }}
  var sessionKey = 'axi_tracker_session_id';
  var sessionId = localStorage.getItem(sessionKey);
  if (!sessionId) {{
    sessionId = 'axi-' + Math.random().toString(36).slice(2) + '-' + Date.now();
    localStorage.setItem(sessionKey, sessionId);
  }}
  var startedAt = Date.now();
  var pagesVisited = Number(sessionStorage.getItem('axi_tracker_pages') || '0') + 1;
  sessionStorage.setItem('axi_tracker_pages', String(pagesVisited));
  function locationData() {{
    var location = window.AXI_TRACKER_LOCATION || {{}};
    return {{
      city: location.city || null,
      state: location.state || null,
      country: location.country || null
    }};
  }}
  function params() {{
    var search = new URLSearchParams(window.location.search);
    var location = locationData();
    return Object.assign({{
      site_id: siteId,
      visitor_id: visitorId,
      session_id: sessionId,
      page_url: window.location.href,
      referrer: document.referrer || null,
      traffic_source: search.get('utm_source') || document.referrer || 'direct',
      device: /Mobi|Android/i.test(navigator.userAgent) ? 'mobile' : 'desktop',
      utm_source: search.get('utm_source'),
      utm_medium: search.get('utm_medium'),
      utm_campaign: search.get('utm_campaign'),
      utm_term: search.get('utm_term'),
      utm_content: search.get('utm_content'),
      pages_visited: pagesVisited
    }}, location);
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
  document.addEventListener('submit', function(event) {{
    var form = event.target;
    if (!form || !form.matches || !form.matches('[data-axi-search]')) return;
    var input = form.querySelector('input[type="search"], input[name="q"], input[name="search"], input[name="query"]');
    send('search', {{ search_query: input ? input.value : null }});
  }}, true);
  window.addEventListener('beforeunload', function() {{
    send('duration', {{ duration_seconds: Math.round((Date.now() - startedAt) / 1000) }});
  }});
  window.AXITracker = {{
    quote: function(value, metadata) {{ send('quote', {{ quote_value: value || null, metadata: metadata || {{}} }}); }},
    reservation: function(value, metadata) {{ send('reservation', {{ reservation_value: value || null, metadata: metadata || {{}} }}); }},
    search: function(query, metadata) {{
      if (typeof query === 'object') {{
        send('search', {{ metadata: query || {{}} }});
      }} else {{
        send('search', {{ search_query: query || null, metadata: metadata || {{}} }});
      }}
    }}
  }};
}})();
"""
    return Response(content=script.strip(), media_type="application/javascript")

from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import QTimer


class AdblockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()
        self.block_hosts = {
            'googleads.g.doubleclick.net',
            'pagead2.googlesyndication.com',
            'stats.g.doubleclick.net',
        }
        self.block_substrings = [
            '/pagead/', '/adservice', '/ads?', '/api/stats/ads',
            'doubleclick.net', 'googlesyndication.com',
        ]

    def interceptRequest(self, info):
        try:
            u = info.requestUrl()
            h = u.host().lower()
            s = u.toString().lower()
            if h in self.block_hosts or any(x in s for x in self.block_substrings):
                info.block(True)
        except Exception:
            pass


_YT_JS = r"""
(function(){
  if (window.__ytABL2) return; window.__ytABL2 = 1;
  function sanitize(o){
    try{
      if(!o||typeof o!=="object") return;
      const ks=['adPlacements','playerAds','adBreaks','adSlots','adSlotMetadata','adParams','adSignatures','ad3Params','adRequest','ads','adSafetyReason','activeViewLogging'];
      for(const k of ks){ if(k in o) delete o[k]; }
      if(o.playerResponse&&typeof o.playerResponse==='object') sanitize(o.playerResponse);
      for(const k in o){ const v=o[k]; if(Array.isArray(v)) for(const e of v) sanitize(e); else if(v&&typeof v==='object') sanitize(v); }
    }catch(e){}
  }
  const ofetch = window.fetch;
  if (ofetch) window.fetch = async function(input, init){
    const r = await ofetch.apply(this, arguments);
    try{
      const url = typeof input==='string'? input : (input&&input.url)||'';
      if(url.includes('/youtubei/') && (url.includes('/player')||url.includes('get_watch')||url.includes('browse'))){
        const c=r.clone(); const ct=c.headers.get('content-type')||'';
        if(ct.includes('json')){ const data=await c.json(); sanitize(data); const text=JSON.stringify(data); return new Response(text,{status:r.status,statusText:r.statusText,headers:r.headers}); }
      }
    }catch(e){}
    return r;
  };
  const xo = XMLHttpRequest.prototype.open;
  const xs = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.open = function(m,u){ this.__abl_u=u; return xo.apply(this, arguments); };
  XMLHttpRequest.prototype.send = function(){ this.addEventListener('readystatechange', ()=>{ if(this.readyState===4){ try{ const url=(this.responseURL||this.__abl_u||''); if(url.includes('/youtubei/') && (url.includes('/player')||url.includes('get_watch')||url.includes('browse'))){ const type=(this.getResponseHeader&&this.getResponseHeader('content-type'))||''; if(type.includes('json')){ const data=JSON.parse(this.responseText); sanitize(data); const text=JSON.stringify(data); Object.defineProperty(this,'responseText',{get(){return text}}); Object.defineProperty(this,'response',{get(){return text}}); } } }catch(e){} } }); return xs.apply(this, arguments); };
  try{ let _ytr=window.ytInitialPlayerResponse||{}; Object.defineProperty(window,'ytInitialPlayerResponse',{configurable:true,get(){return _ytr;},set(v){ try{sanitize(v);}catch(e){} _ytr=v; }});}catch(e){}
  function ui(){ try{ document.querySelectorAll('.ytp-ad-overlay-close-button').forEach(b=>b.click()); const s=document.querySelector('.ytp-ad-skip-button, .ytp-ad-skip-button-modern'); if(s) s.click(); if(!document.getElementById('yt-abl-css')){ const se=document.createElement('style'); se.id='yt-abl-css'; se.textContent='#player-ads,.video-ads,#masthead-ad,ytd-display-ad-renderer,ytd-promoted-sparkles-web-renderer,ytd-in-feed-ad-layout-renderer,ytd-action-companion-ad-renderer,ytd-companion-slot-renderer,ytd-video-masthead-ad-v3-renderer,.ytd-watch-next-secondary-results-renderer[modern-ads],.ytp-ad-module,.ytp-ad-image-overlay,.ytp-ad-overlay-slot,.ytp-ad-player-overlay,ytd-enforcement-message-view-model,ytd-enforcement-message-renderer,tp-yt-paper-dialog.ytd-popup-container,#ad,#ads{display:none!important;visibility:hidden!important;opacity:0!important;height:0!important}'; document.documentElement.appendChild(se);} }catch(e){} }
  ui();
  window.addEventListener('yt-navigate-finish', ()=>setTimeout(()=>ui(),100));
  document.addEventListener('readystatechange', ()=>{ if(document.readyState==='interactive') setTimeout(()=>ui(),100); });
  setInterval(ui, 1000);
})();
"""


def enable_adblock(view, target="youtube"):
    try:
        if getattr(view, "_adblock_enabled", False):
            return
        page = view.page()
        prof = page.profile()
        setter = getattr(prof, 'setUrlRequestInterceptor', None) or getattr(prof, 'setRequestInterceptor', None)
        if callable(setter):
            interceptor = AdblockInterceptor()
            setter(interceptor)
            setattr(view, "_adblock_interceptor", interceptor)

        def inject():
            try:
                p = view.page()
                u = p.url().toString().lower() if hasattr(p, 'url') else ''
                host = ''
                try:
                    host = p.url().host().lower()
                except Exception:
                    pass
                if target == 'youtube' or ('youtube' in host):
                    p.runJavaScript(_YT_JS)
            except Exception:
                pass

        def schedule():
            try:
                inject()
                for ms in (250, 500, 1000, 2000):
                    QTimer.singleShot(ms, inject)
            except Exception:
                pass

        try:
            view._adblock_load_cb = lambda ok: ok and schedule()
            view.loadFinished.connect(view._adblock_load_cb)
        except Exception:
            pass
        try:
            view._adblock_url_cb = lambda _u: schedule()
            view.urlChanged.connect(view._adblock_url_cb)
        except Exception:
            pass
        try:
            view._adblock_start_cb = lambda: schedule()
            view.loadStarted.connect(view._adblock_start_cb)
        except Exception:
            pass

        try:
            t = getattr(view, '_adblock_timer', None)
            if t is None:
                t = QTimer(view)
                t.setInterval(1500)
                t.timeout.connect(inject)
                t.start()
                setattr(view, '_adblock_timer', t)
        except Exception:
            pass

        setattr(view, "_adblock_enabled", True)
    except Exception:
        pass

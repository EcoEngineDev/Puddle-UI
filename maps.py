from __future__ import annotations
import os
from typing import Tuple
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

__all__ = ["MapsWidget"]


class _GeoPage(QWebEnginePage):
    def featurePermissionRequested(self, o, f):
        self.setFeaturePermission(
            o, f,
            QWebEnginePage.PermissionGrantedByUser
            if f == QWebEnginePage.Geolocation
            else QWebEnginePage.PermissionDeniedByUser
        )


class MapsWidget(QWebEngineView):
    _HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="initial-scale=1,width=device-width">
<style>
 html,body{{height:100%;margin:0}}
 #map{{height:100%}}
 #controls{{position:absolute;top:8px;left:50%;transform:translateX(-50%);
           z-index:6;background:#fff;padding:4px;border-radius:4px;display:flex}}
 #dest{{width:260px;border:1px solid #ccc;padding:4px}}
 #go{{padding:4px 10px;border:1px solid #ccc;background:#4285f4;color:#fff;cursor:pointer}}
 #results{{position:absolute;top:44px;left:50%;transform:translateX(-50%);
           z-index:5;width:320px;max-height:240px;overflow:auto;background:#fff;
           border:1px solid #ccc;display:none}}
 .res{{padding:6px 8px;cursor:pointer}} .res:hover{{background:#eee}}
 #panel{{position:absolute;right:0;top:0;bottom:0;width:320px;overflow:auto;
         background:#111;color:#eee;padding:8px;font-family:sans-serif}}
 .step{{margin-bottom:6px;padding-bottom:6px;border-bottom:1px solid #333}}
 /* --- re‑center button --- */
 #recenter{{position:absolute;bottom:20px;right:20px;width:44px;height:44px;
           border-radius:50%;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.3);
           display:flex;align-items:center;justify-content:center;cursor:pointer;z-index:6}}
 #recenter:hover{{background:#eee}}
</style>
<script src="https://maps.googleapis.com/maps/api/js?key={api_key}"></script>
</head><body>
<div id="map"></div>
<div id="panel"></div>
<div id="controls"><input id="dest" placeholder="Where to?"><button id="go" disabled>Go</button></div>
<div id="results"></div>
<div id="recenter" title="Back to me">⌖</div>
<script>
 let map,directionsService,directionsRenderer,origin=null,userMarker=null,navigating=false;
 const arrowIcon={{path:google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale:6,
                   fillColor:'#4285f4',fillOpacity:1,strokeColor:'#fff',strokeWeight:1}};
 const panel=document.getElementById('panel'); const goBtn=document.getElementById('go');
 const resultsBox=document.getElementById('results'); const recBtn=document.getElementById('recenter');

 function updateUserMarker(lat,lng,hd=0){{
   const pos={{lat,lng}};
   if(!userMarker){{
     userMarker=new google.maps.Marker({{position:pos,map,
       icon:{{...arrowIcon,rotation:hd}}}});
   }}else{{
     userMarker.setPosition(pos);
     userMarker.setIcon({{...arrowIcon,rotation:hd}});
   }}
   if(navigating){{ map.panTo(pos); map.setZoom(18); }}
 }}

 function recenter(){{        // called on button click
   if(origin){{ map.panTo(origin); map.setZoom(18); navigating=true; }}
 }}
 recBtn.onclick=recenter;

 function init(){{
   map=new google.maps.Map(document.getElementById('map'),{{center:{{lat:{lat},lng:{lng}}},
         zoom:18,disableDefaultUI:true,gestureHandling:'greedy',mapId:'{map_id}'}});

   directionsService=new google.maps.DirectionsService();
   directionsRenderer=new google.maps.DirectionsRenderer({{map,panel,
       suppressMarkers:false,polylineOptions:{{strokeWeight:6}}}});

   if(navigator.geolocation){{
     navigator.geolocation.watchPosition(p=>{{
       origin={{lat:p.coords.latitude,lng:p.coords.longitude}};
       updateUserMarker(origin.lat,origin.lng,p.coords.heading||0);
       goBtn.disabled=false;
     }}, err=>{{console.warn('GPS denied',err);}}, {{enableHighAccuracy:true}});
   }}

   async function fetchIP(){{
     try{{
       const r=await fetch('https://ipapi.co/json/');
       const j=await r.json();
       if(j.latitude){{
         origin={{lat:+j.latitude,lng:+j.longitude}};
         updateUserMarker(origin.lat,origin.lng);
         goBtn.disabled=false;
       }}
     }}catch(e){{console.error(e);}}
   }}
   fetchIP(); setInterval(fetchIP,30000);

   goBtn.onclick=searchPlaces;
   document.getElementById('dest').addEventListener('keydown',e=>{{if(e.key==='Enter')searchPlaces();}});
 }}

 async function searchPlaces(){{
   const query=document.getElementById('dest').value.trim();
   if(!query) return;
   resultsBox.innerHTML=''; resultsBox.style.display='block';
   try{{
     const url='https://places.googleapis.com/v1/places:searchText?key={api_key}';
     const r=await fetch(url,{{method:'POST',
       headers:{{'Content-Type':'application/json',
                 'X-Goog-FieldMask':'places.displayName,places.location'}},
       body:JSON.stringify({{textQuery:query,maxResultCount:8,languageCode:'en'}})}} );
     const j=await r.json();
     if(!j.places){{resultsBox.innerHTML='<div class=res>No results</div>';return;}}
     j.places.forEach(pl=>{{
       const div=document.createElement('div'); div.className='res'; div.textContent=pl.displayName.text;
       div.onclick=()=>{{ resultsBox.style.display='none';
                          routeTo(pl.location.latitude,pl.location.longitude); }};
       resultsBox.appendChild(div);
     }});
   }}catch(e){{resultsBox.innerHTML='<div class=res>'+e+'</div>';}}
 }}

 function routeTo(lat,lng){{
   const dest={{lat,lng}};
   navigating=true;
   directionsService.route({{origin:origin||map.getCenter(),destination:dest,
     travelMode:google.maps.TravelMode.DRIVING}})
     .then(r=>{{ directionsRenderer.setDirections(r); map.setZoom(18); }})
     .catch(e=>panel.innerHTML='<p class="step">'+e.message+'</p>');
 }}

 window.init=init; init();
</script></body></html>"""

    def __init__(
        self,
        api_key: str | None = None,
        center: Tuple[float, float] = (40.758, -73.9855),
        zoom: int = 12,
        map_id: str = ""
    ) -> None:
        super().__init__()
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY", "YOUR_API_KEY")
        self.setPage(_GeoPage(self))
        self.setHtml(
            self._HTML.format(api_key=self.api_key, lat=center[0], lng=center[1], map_id=map_id),
            QUrl("https://localhost/")
        )

    def show_route(self, origin: str, destination: str) -> None:
        self.page().runJavaScript(
            ("navigating=true; directionsService.route({origin:'%s',destination:'%s',"
             "travelMode:google.maps.TravelMode.DRIVING})"
             ".then(r=>{directionsRenderer.setDirections(r); map.setZoom(18);});")
            % (origin, destination)
        )

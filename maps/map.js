let map,
  directionsService,
  directionsRenderer,
  origin = null,
  userMarker = null,
  navigating = false,
  placesService;

function toRad(d) {
  return (d * Math.PI) / 180;
}

function dist(a, b) {
  const φ1 = toRad(a.lat),
    φ2 = toRad(b.lat),
    dφ = φ2 - φ1,
    dλ = toRad(b.lng - a.lng),
    h =
      Math.sin(dφ / 2) ** 2 +
      Math.cos(φ1) * Math.cos(φ2) * Math.sin(dλ / 2) ** 2;
  return 2 * 6371000 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
}

function bearing(a, b) {
  const φ1 = toRad(a.lat),
    φ2 = toRad(b.lat),
    y = Math.sin(toRad(b.lng - a.lng)) * Math.cos(φ2),
    x =
      Math.cos(φ1) * Math.sin(φ2) -
      Math.sin(φ1) * Math.cos(φ2) * Math.cos(toRad(b.lng - a.lng));
  return ((Math.atan2(y, x) * 180) / Math.PI + 360) % 360;
}

function updateUser(lat, lng, hd = 0) {
  const pos = { lat, lng },
    icon = {
      path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
      scale: 6,
      fillColor: "#4285f4",
      fillOpacity: 1,
      strokeColor: "#fff",
      strokeWeight: 1,
      rotation: hd,
    };
  if (!userMarker) {
    userMarker = new google.maps.Marker({ map, position: pos, icon });
  } else {
    userMarker.setPosition(pos);
    userMarker.setIcon(icon);
  }
  if (navigating) {
    map.panTo(pos);
    map.setZoom(18);
  }
}

function recenter() {
  if (origin) {
    navigating = true;
    map.panTo(origin);
    map.setZoom(10);
  }
}

function rotateCW() {
  map.setHeading(((map.getHeading() || 0) + 90) % 360);
}

async function searchPlaces() {
  const q = document.getElementById("dest").value.trim();
  if (!q) return;

  const results = document.getElementById("results");
  results.innerHTML = "";
  results.style.display = "block";

  placesService.textSearch({ query: q }, (pls, status) => {
    if (status !== google.maps.places.PlacesServiceStatus.OK) {
      results.innerHTML = '<div class="res">No results</div>';
      return;
    }
    pls.forEach((pl) => {
      const div = document.createElement("div");
      div.className = "res";
      div.textContent = pl.name;
      div.onclick = () => {
        results.style.display = "none";
        showInfo(pl.place_id, pl.geometry.location);
      };
      results.appendChild(div);
    });
  });
}

function showInfo(placeId, location) {
  placesService.getDetails(
    {
      placeId: placeId,
      fields: [
        "name",
        "formatted_address",
        "formatted_phone_number",
        "rating",
        "user_ratings_total",
        "opening_hours",
        "geometry",
        "photos",
        "website",
        "types",
      ],
    },
    (place, status) => {
      if (status !== google.maps.places.PlacesServiceStatus.OK) return;

      const box = document.getElementById("infoBox");
      box.innerHTML = "";

      if (place.photos && place.photos.length) {
        const img = document.createElement("img");
        img.src = place.photos[0].getUrl({ maxWidth: 300 });
        box.appendChild(img);
      }

      const d = document.createElement("div");
      d.className = "details";

      const h2 = document.createElement("h2");
      h2.textContent = place.name;
      d.appendChild(h2);

      if (place.rating != null) {
        const rd = document.createElement("div");
        rd.className = "rating";
        rd.textContent =
          place.rating + " ★ (" + (place.user_ratings_total || 0) + ")";
        d.appendChild(rd);
      }

      if (place.types && place.types.length) {
        const t = document.createElement("p");
        t.textContent = place.types[0].replace(/_/g, " ");
        d.appendChild(t);
      }

      if (place.formatted_address) {
        const a = document.createElement("p");
        a.textContent = place.formatted_address;
        d.appendChild(a);
      }

      if (place.formatted_phone_number) {
        const p = document.createElement("p");
        p.textContent = place.formatted_phone_number;
        d.appendChild(p);
      }

      box.appendChild(d);

      const btn = document.createElement("button");
      btn.className = "directions-btn";
      btn.textContent = "Directions";
      btn.onclick = () => {
        box.style.display = "none";
        routeTo(location);
      };
      box.appendChild(btn);

      box.style.display = "block";
    }
  );
}

function routeTo(dest) {
  navigating = true;
  directionsService
    .route({
      origin: origin || map.getCenter(),
      destination: dest,
      travelMode: google.maps.TravelMode.DRIVING,
    })
    .then((r) => {
      directionsRenderer.setDirections(r);
      displayNextTurn(r.routes[0].legs[0].steps[0]);
    })
    .catch(console.error);
}

function displayNextTurn(step) {
  const box = document.getElementById("nextTurn"),
    arc = step.maneuver || "",
    arrow = arc.includes("left") ? "←" : arc.includes("right") ? "→" : "↑",
    text = step.instructions.replace(/<[^>]+>/g, ""),
    distMi = (step.distance.value / 1609.34).toFixed(2) + " mi";

  box.innerHTML = `<span class="arrow">${arrow}</span> ${text} — ${distMi}`;
  box.style.display = "block";
}

function init() {
    placesService = new google.maps.places.PlacesService(map);

  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: INITIAL_LAT, lng: INITIAL_LNG },
    zoom: 18,
    disableDefaultUI: true,
    gestureHandling: "greedy",
    mapId: MAP_ID,
  });

  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer({
    map,
    polylineOptions: { strokeWeight: 6 },
  });


  if (navigator.geolocation) {
    navigator.geolocation.watchPosition(
      (p) => {
        origin = { lat: p.coords.latitude, lng: p.coords.longitude };
        updateUser(origin.lat, origin.lng, p.coords.heading || 0);
        document.getElementById("go").disabled = false;
      },
      console.warn,
      { enableHighAccuracy: true }
    );
  }
  
  (async function ipFallback() {
    try {
      const r = await fetch("https://ipapi.co/json/");
      const j = await r.json();
      if (j.latitude) {
        origin = { lat: +j.latitude, lng: +j.longitude };
        updateUser(origin.lat, origin.lng);
        document.getElementById("go").disabled = false;
      }
    } catch {}
  })();
  recenter;
  document.getElementById("recenter").onclick = recenter;
  document.getElementById("rotate").onclick = rotateCW;
  document.getElementById("go").onclick = searchPlaces;
  document.getElementById("dest").addEventListener("keydown", (e) => {
    if (e.key === "Enter") searchPlaces();
  });
}

window.init = init;
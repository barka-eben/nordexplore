// Carte des hébergements : la liste fonctionne hors ligne, la carte nécessite Leaflet + OpenStreetMap.
(function () {
  var el = document.getElementById("carte");
  var liste = document.getElementById("liste-carte");
  if (!el) return;
  fetch(el.dataset.url)
    .then(function (r) { return r.json(); })
    .then(function (data) {
      data.resultats.forEach(function (x) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = x.url; a.textContent = x.nom;
        li.appendChild(a);
        li.appendChild(document.createTextNode(" · " + x.etoiles + "★ · score " + x.score + "/100 · " + x.explication));
        liste.appendChild(li);
      });
      if (!data.resultats.length) {
        var p = document.createElement("li");
        p.textContent = "Aucun hébergement ne correspond à ces critères.";
        liste.appendChild(p);
      }
      if (typeof L === "undefined") {
        el.textContent = "Carte indisponible (hors ligne) : utilisez la liste ci-dessous.";
        el.classList.add("hors-ligne");
        return;
      }
      var map = L.map(el);
      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 18, attribution: "© OpenStreetMap"
      }).addTo(map);
      var pts = [];
      data.resultats.forEach(function (x) {
        var box = document.createElement("div");
        var a = document.createElement("a");
        a.href = x.url; a.textContent = x.nom;
        box.appendChild(a);
        box.appendChild(document.createElement("br"));
        box.appendChild(document.createTextNode(x.etoiles + "★ · " + x.score + "/100 · " + Math.round(x.tarif) + " FCFA"));
        L.marker([x.lat, x.lon], { title: x.nom }).addTo(map).bindPopup(box);
        pts.push([x.lat, x.lon]);
      });
      if (pts.length) map.fitBounds(pts, { padding: [30, 30], maxZoom: 14 });
      else map.setView([9.3014, 13.3977], 11);
    })
    .catch(function () { el.textContent = "Impossible de charger les résultats."; });
})();

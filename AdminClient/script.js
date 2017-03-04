var atRiskUsers = L.layerGroup([]);
var goodUsers = L.layerGroup([]);
var clusters = L.layerGroup([]);


var mymap = L.map('mapid', {
    layers: [atRiskUsers, goodUsers, clusters]}).setView([51.505, -0.09], 8);

    var overlayMaps = {
        "Users - At Risk": atRiskUsers,
        "Users - Safe": goodUsers,
        "Clusters": clusters
    };
L.control.layers(null,overlayMaps).addTo(mymap);


L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
  maxZoom: 18,
  attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
  '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
  'Imagery © <a href="http://mapbox.com">Mapbox</a>',
  id: 'mapbox.streets'
}).addTo(mymap);

function getData(){

  $.ajax({
    method: "GET",
    url: 'http://10.192.151.191:8080/cluster'
  }).done(function(msg) {

    console.log(msg);
    $.each(msg, function(idx, val){
      //console.log(idx);
      //console.log(val);
      var totalLat = 0;
      var totalLon = 0;
      var i = 0;
      var color, fillCol;
      var layer = null;
      if (idx < 0){
        color = 'green';
        fillCol = '#00ff38';
        layerUsers = goodUsers;
      }
      else{
        color = 'red';
        fillCol = '#f03';
        layerUsers = atRiskUsers;
      }
      val.forEach(function(val2){
        totalLat += parseFloat(val2.lat);
        totalLon += parseFloat(val2.lon);
        i ++;
        pintarUser(parseFloat(val2.lon).toFixed(10), parseFloat(val2.lat).toFixed(10), color, fillCol, layerUsers);
      });
      if (idx != -1 && idx != 0) pintar(parseFloat(totalLon/i).toFixed(10),parseFloat(totalLat/i).toFixed(10), color, fillCol);
    });

    //console.log(msg);
  });
  /*
  this.$http.get('http://10.192.151.191:8080/cluster').then(function (response) {
    // get body data
    //this.clusterData = response.body;


  }, function (response) {
    console.log(response);
    // error callback
  });
  */
}

function pintarUser(lat,lon, col, fillCol, layerUsers){
  L.circle([lat, lon], 10, {
    color: col,
    fillColor: fillCol,
    fillOpacity: 0.2
  }).addTo(layerUsers).bindPopup("I am a circle.");
}

function pintar(lat,lon,col,fillCol){
  console.log(lat+"-"+lon);
  L.circle([lat, lon], 600, {
    color: col,
    fillColor: fillCol,
    fillOpacity: 0.2
  }).addTo(clusters).bindPopup("I am a circle.");
}

window.onload = function() {
  getData();
};

/*
window.setInterval(function(){
app.actualizar();
}, 5000);
*/

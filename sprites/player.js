/* Real-time sprite player for the 5BX workout screen.
   Uses the transparent poses extracted from video/sheets/.
   Drives #sprite-img inside the existing #sprite-player container. */
(function () {
  var CYCLES = {
    ex1: [1, 2, 1, 3],
    ex2: [1, 2, 3, 2],
    ex3: [1, 2, 1, 3],
    ex4: [1, 2, 3, 2],
    run: [1, 2, 3, 4],
    jump: [1, 2, 3, 2]
  };
  var timer = null;
  var currentKey = null;

  function start(key, cycleSeconds) {
    var player = document.getElementById('sprite-player');
    var img = document.getElementById('sprite-img');
    if (!player || !img || !CYCLES[key]) return;
    stop();
    currentKey = key;
    var cycle = CYCLES[key];
    var per = (cycleSeconds || 1.2) / cycle.length * 1000;
    var i = 0;
    function tick() {
      var n = cycle[i];
      img.src = 'sprites/' + key + '-p' + n + '.png';
      img.alt = key + ' pose ' + n;
      i = (i + 1) % cycle.length;
    }
    tick();
    timer = setInterval(tick, per);
    player.hidden = false;
    var figImg = document.getElementById('fig-img');
    if (figImg) figImg.hidden = true;
  }

  function stop() {
    if (timer) { clearInterval(timer); timer = null; }
    currentKey = null;
    var player = document.getElementById('sprite-player');
    if (player) player.hidden = true;
    var figImg = document.getElementById('fig-img');
    if (figImg) figImg.hidden = false;
  }

  window.SpritePlayer = { start: start, stop: stop };
})();

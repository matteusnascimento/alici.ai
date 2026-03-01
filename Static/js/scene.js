/**
 * scene.js — ALICI v3.0 3D Neural Network Background
 * Optimized Canvas WebGL-style neural network particle system.
 * Does not block scroll or interactions.
 */

(function () {
  const canvas = document.getElementById('neural-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let W, H, animId;
  let nodes = [];
  const NODE_COUNT = 60;
  const CONNECTION_DIST = 140;
  const COLORS = ['#00ffff', '#0066ff', '#9933ff', '#ff0099', '#00ff88'];

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function randomColor() {
    return COLORS[Math.floor(Math.random() * COLORS.length)];
  }

  function initNodes() {
    nodes = [];
    for (let i = 0; i < NODE_COUNT; i++) {
      nodes.push({
        x: Math.random() * W,
        y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        r: Math.random() * 2.5 + 1,
        color: randomColor(),
        pulse: Math.random() * Math.PI * 2,
        pulseSpeed: 0.02 + Math.random() * 0.02,
      });
    }
  }

  function drawFrame() {
    ctx.clearRect(0, 0, W, H);

    // Update node positions
    for (const n of nodes) {
      n.x += n.vx;
      n.y += n.vy;
      n.pulse += n.pulseSpeed;

      if (n.x < 0 || n.x > W) n.vx *= -1;
      if (n.y < 0 || n.y > H) n.vy *= -1;
    }

    // Draw connections
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < CONNECTION_DIST) {
          const alpha = (1 - dist / CONNECTION_DIST) * 0.35;
          ctx.beginPath();
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(nodes[j].x, nodes[j].y);
          ctx.strokeStyle = `rgba(0, 200, 255, ${alpha})`;
          ctx.lineWidth = 0.6;
          ctx.stroke();
        }
      }
    }

    // Draw nodes
    for (const n of nodes) {
      const glow = Math.sin(n.pulse) * 0.5 + 0.5;
      const radius = n.r * (1 + glow * 0.5);

      const grad = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, radius * 4);
      grad.addColorStop(0, n.color);
      grad.addColorStop(1, 'transparent');

      ctx.beginPath();
      ctx.arc(n.x, n.y, radius, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.fill();

      // Outer glow
      ctx.beginPath();
      ctx.arc(n.x, n.y, radius * 3, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(0, 200, 255, ${glow * 0.05})`;
      ctx.fill();
    }

    animId = requestAnimationFrame(drawFrame);
  }

  function start() {
    resize();
    initNodes();
    drawFrame();
  }

  function stop() {
    if (animId) cancelAnimationFrame(animId);
  }

  window.addEventListener('resize', () => {
    resize();
    initNodes();
  });

  // Pause when tab is hidden to save resources
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) stop();
    else drawFrame();
  });

  start();

  // Expose for external control
  window.NeuralScene = { start, stop };
})();

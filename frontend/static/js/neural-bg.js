/**
 * neural-bg.js — Canvas-based neural network particle background.
 *
 * 75 particles connected by proximity lines.
 * Adapts colours to dark/light theme via CSS variables.
 * Non-blocking: uses requestAnimationFrame and pointer-events: none.
 */

(function () {
  const PARTICLE_COUNT = 75;
  const MAX_DISTANCE = 140;
  const SPEED = 0.45;

  let canvas, ctx, particles, animId;
  let themeColors = getThemeColors();

  function getThemeColors() {
    const theme = document.documentElement.getAttribute("data-theme") || "dark";
    return theme === "light"
      ? { particle: "rgba(6,182,212,", line: "rgba(6,182,212," }
      : { particle: "rgba(34,211,238,", line: "rgba(34,211,238," };
  }

  function createParticle() {
    return {
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * SPEED,
      vy: (Math.random() - 0.5) * SPEED,
      radius: Math.random() * 1.8 + 0.5,
      opacity: Math.random() * 0.5 + 0.25,
    };
  }

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Move and wrap particles
    particles.forEach((p) => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0) p.x = canvas.width;
      else if (p.x > canvas.width) p.x = 0;
      if (p.y < 0) p.y = canvas.height;
      else if (p.y > canvas.height) p.y = 0;
    });

    // Draw connections
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < MAX_DISTANCE) {
          const alpha = (1 - dist / MAX_DISTANCE) * 0.35;
          ctx.beginPath();
          ctx.strokeStyle = `${themeColors.line}${alpha})`;
          ctx.lineWidth = 0.7;
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }

    // Draw particles
    particles.forEach((p) => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = `${themeColors.particle}${p.opacity})`;
      ctx.fill();
    });

    animId = requestAnimationFrame(draw);
  }

  function init(canvasElement) {
    canvas = canvasElement;
    ctx = canvas.getContext("2d");
    canvas.style.pointerEvents = "none";

    resize();
    particles = Array.from({ length: PARTICLE_COUNT }, createParticle);

    window.addEventListener("resize", resize);
    draw();
  }

  function updateTheme() {
    themeColors = getThemeColors();
  }

  function destroy() {
    if (animId) cancelAnimationFrame(animId);
    window.removeEventListener("resize", resize);
  }

  // Public API
  window.NeuralBg = { init, updateTheme, destroy };
})();

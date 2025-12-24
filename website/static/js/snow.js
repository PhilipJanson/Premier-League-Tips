document.addEventListener('DOMContentLoaded', function () {
  const container = document.getElementById('holiday-snow');
  if (!container) return;

  const FLAKE_COUNT = 50;

  for (let i = 0; i < FLAKE_COUNT; i++) {
    const flake = document.createElement('div');
    flake.className = 'snowflake';
    flake.textContent = '❄';

    // Size: 12-24px
    const size = Math.random() * 12 + 12;
    flake.style.fontSize = size + 'px';

    // Random horizontal position
    flake.style.left = Math.random() * 100 + '%';

    // Fall duration: 6-14s
    const duration = Math.random() * 8 + 6;
    flake.style.setProperty('--fall-duration', duration + 's');

    // Sway amount: -40px to 40px
    const sway = Math.random() * 80 - 40;
    flake.style.setProperty('--sway', sway + 'px');

    // Rotation speed multiplier
    const rotation = Math.random() * 1 + 0.5;
    flake.style.setProperty('--rotation', rotation);

    // Opacity 0.4 - 1.0
    flake.style.opacity = (0.4 + Math.random() * 0.6).toFixed(2);

    // Stagger start
    flake.style.animationDelay = Math.random() * -duration + 's';

    // Slight color variation: white to soft blue
    const blueTint = Math.floor(Math.random() * 60); // 0-59
    flake.style.color = `rgb(255, 255, ${200 + blueTint})`;

    container.appendChild(flake);
  }
});

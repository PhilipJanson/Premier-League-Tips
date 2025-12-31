document.addEventListener('DOMContentLoaded', () => {
  function tipButtonPressed(tips, csrfToken) {
    fetch('/register-tips', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify(tips),
    }).then((_res) => {
      tips = [];
      window.location.href = '/tip/register';
    });
  }

  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute('content');
  let tips = [];

  // Tip button clicks
  document.querySelectorAll('[id^="tipbutton-"]').forEach((button) => {
    button.addEventListener('click', () => {
      if (button.dataset.enabled !== 'true') return;

      const parts = button.id.split('-');
      const fixtureId = parts[1];
      const value = parts.slice(2).join('-');

      const radios = document.getElementsByName(`${fixtureId}-buttons`);
      for (const r of radios) {
        r.checked = false;
      }
      const input = document.getElementById(`${fixtureId}-tips-${value}`);
      if (input) input.checked = true;

      for (const r of radios) {
        const lab = document.querySelector(`label[for="${r.id}"]`);
        if (lab) lab.classList.remove('active');
      }
      button.classList.add('active');

      tips = tips.filter((t) => t.fixtureId !== fixtureId);
      tips.push({ fixtureId, value });

      document.getElementById('nav-bottom-button').classList.add('visible');
    });
  });

  // Submit button
  document
    .getElementById('tip-button-submit')
    .addEventListener('click', () => tipButtonPressed(tips, csrfToken));
});

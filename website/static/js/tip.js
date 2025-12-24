document.addEventListener('DOMContentLoaded', () => {
  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute('content');
  let tips = [];

  // Tip button clicks
  document.querySelectorAll('[id^="tipbutton-"]').forEach((button) => {
    button.addEventListener('click', () => {
      if (button.dataset.enabled !== 'true') return;

      const [_, fixtureId, value] = button.id.split('-');
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

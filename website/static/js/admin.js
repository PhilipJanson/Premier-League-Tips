document.addEventListener('DOMContentLoaded', () => {
  function triggerAdminAction(endpoint, csrfToken) {
    fetch(endpoint, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
      },
    }).then((_res) => {
      window.location.href = '/admin';
    });
  }

  function setActiveSeason(csrfToken) {
    const season = document.getElementById('set-active-season-select').value;
    if (!season) return;
    fetch('/admin/set-active-season', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ season: season }),
    }).then((_res) => {
      window.location.href = '/admin';
    });
  }

  function addSeason(csrfToken) {
    const season = document.getElementById('add-season-input').value;
    if (!season) return;
    fetch('/admin/add-season', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ season: season }),
    }).then((_res) => {
      window.location.href = '/admin';
    });
  }

  function setUserAdmin(csrfToken) {
    const uuid = document.getElementById('user-uuid-input').value;
    if (!uuid) return;
    fetch('/admin/set-user-admin', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ uuid: uuid }),
    }).then((_res) => {
      window.location.href = '/admin';
    });
  }

  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute('content');

  // Register button event listeners
  document
    .getElementById('button-fetch-api-fixtures')
    .addEventListener('click', () =>
      triggerAdminAction('/admin/fetch-api-fixtures', csrfToken)
    );
  document
    .getElementById('button-fetch-api-standings')
    .addEventListener('click', () =>
      triggerAdminAction('/admin/fetch-api-standings', csrfToken)
    );
  document
    .getElementById('button-calculate-results')
    .addEventListener('click', () =>
      triggerAdminAction('/admin/calculate-results', csrfToken)
    );
  document
    .getElementById('button-toggle-late-modification')
    .addEventListener('click', () =>
      triggerAdminAction('/admin/toggle-late-modification', csrfToken)
    );
  document
    .getElementById('button-set-active-season')
    .addEventListener('click', () => setActiveSeason(csrfToken));
  document
    .getElementById('button-add-season')
    .addEventListener('click', () => addSeason(csrfToken));
  document
    .getElementById('button-set-user-admin')
    .addEventListener('click', () => setUserAdmin(csrfToken));
  document
    .getElementById('button-toggle-holiday-theme')
    .addEventListener('click', () =>
      triggerAdminAction('/admin/toggle-holiday-theme', csrfToken)
    );
});

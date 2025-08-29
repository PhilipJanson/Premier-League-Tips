function triggerAdminAction(endpoint) {
  fetch(endpoint, {
    method: 'POST',
  }).then((_res) => {
    window.location.href = '/admin';
  });
}

function addSeason() {
  const season = document.getElementById('add-season-input').value;
  if (!season) return;
  fetch('/admin/add-season', {
    method: 'POST',
    body: JSON.stringify(season),
  }).then((_res) => {
    window.location.href = '/admin';
  });
}

function setActiveSeason() {
  const season = document.getElementById('set-active-season-select').value;
  if (!season) return;
  fetch('/admin/set-active-season', {
    method: 'POST',
    body: JSON.stringify(season),
  }).then((_res) => {
    window.location.href = '/admin';
  });
}

function setUserAdmin() {
  const uuid = document.getElementById('user-uuid-input').value;
  if (!uuid) return;
  fetch('/admin/set-user-admin', {
    method: 'POST',
    body: JSON.stringify(uuid),
  }).then((_res) => {
    window.location.href = '/admin';
  });
}

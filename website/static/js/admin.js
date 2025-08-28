function fetchApiFixtures() {
  fetch('/admin/fetch-api-fixtures', {
    method: 'POST',
  }).then((_res) => {
    tips = [];
    window.location.href = '/admin';
  });
}

function fetchApiStandings() {
  fetch('/admin/fetch-api-standings', {
    method: 'POST',
  }).then((_res) => {
    tips = [];
    window.location.href = '/admin';
  });
}

function calculateResults() {
  fetch('/admin/calculate-results', {
    method: 'POST',
  }).then((_res) => {
    tips = [];
    window.location.href = '/admin';
  });
}

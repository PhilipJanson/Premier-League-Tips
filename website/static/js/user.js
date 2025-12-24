const csrfToken = document
  .querySelector('meta[name="csrf-token"]')
  .getAttribute('content');

function setFavoriteTeam(user_id) {
  const teamId = document.getElementById('set-favorite-team-select').value;
  if (!teamId) {
    console.log('team.id was null');
    return;
  }

  fetch(`/user/${user_id}/set-favorite-team`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({ teamId: teamId }),
  }).then((_res) => {
    window.location.href = `/user/${user_id}`;
  });
}

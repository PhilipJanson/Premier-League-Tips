document.addEventListener('DOMContentLoaded', () => {
  function setFavoriteTeam(userId, csrfToken) {
    const teamId = document.getElementById('set-favorite-team-select').value;
    if (!teamId) {
      console.log('teamId was null');
      return;
    }

    fetch(`/user/${userId}/set-favorite-team`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ teamId: teamId }),
    }).then((_res) => {
      window.location.href = `/user/${userId}`;
    });
  }

  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    .getAttribute('content');
  const button = document.getElementById('button-set-favorite-team');
  const uuid = button.dataset.uuid;
  button.addEventListener('click', () => setFavoriteTeam(uuid, csrfToken));
});

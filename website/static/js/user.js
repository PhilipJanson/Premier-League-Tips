document.addEventListener('DOMContentLoaded', () => {
  function setFavoriteTeam(userId, csrfToken) {
    const teamId = document.getElementById('set-favorite-team-select').value;
    if (!teamId) {
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
  const userIdElement = document.getElementById('user-id');
  const userId = userIdElement.dataset.uuid;

  const favoriteTeamButton = document.getElementById(
    'button-set-favorite-team'
  );
  favoriteTeamButton.addEventListener('click', () =>
    setFavoriteTeam(userId, csrfToken)
  );

  const changePasswordButton = document.getElementById(
    'button-change-password'
  );
  changePasswordButton.addEventListener(
    'click',
    () => (window.location.href = `/user/${userId}/change-password`)
  );
});

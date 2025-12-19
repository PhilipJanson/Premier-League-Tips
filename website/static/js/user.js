function setFavoriteTeam(user_id) {
  const team_id = document.getElementById('set-favorite-team-select').value;
  if (!team_id) {
    console.log("team.id was null")
    return;
  }
  fetch(`/user/${user_id}/set-favorite-team`, {
    method: 'POST',
    body: JSON.stringify(team_id),
  }).then((_res) => {
    window.location.href = `/user/${user_id}`;
  });
}
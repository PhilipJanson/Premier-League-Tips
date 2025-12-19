var carousels = document.getElementsByClassName('carousel');

for (const carousel of carousels) {
  const userId = carousel.dataset.userId;
  const total = Number(carousel.dataset.total) || 0;

  const correctCtx = document.getElementById(`${userId}-correct-chart`);
  const correct = Number(correctCtx?.dataset?.correct) || 0;
  const incorrect = Number(correctCtx?.dataset?.incorrect) || 0;
  const finished = Number(correctCtx?.dataset?.finished) || 0;
  const notPlayed = Math.max(0, total - finished);

  function safePercent(part, tot) {
    if (!tot || tot === 0) return '0%';
    return Math.round((100 * part) / tot) + '%';
  }

  var correctPieChart = new Chart(correctCtx.getContext('2d'), {
    type: 'pie',
    data: {
      labels: [
        'Antal rätt ' + safePercent(correct, total),
        'Antal fel ' + safePercent(incorrect, total),
        'Ej spelade ' + safePercent(notPlayed, total),
      ],
      datasets: [
        {
          data: [correct, incorrect, notPlayed],
          backgroundColor: ['#46BFBD', '#F7464A', '#FDB45C'],
          hoverBackgroundColor: ['#5AD3D1', '#FF5A5E', '#FFC870'],
        },
      ],
    },
    options: { responsive: true },
  });

  const tipCtx = document.getElementById(`${userId}-tip-chart`);
  const tip1 = Number(tipCtx?.dataset?.tipOne) || 0;
  const tipX = Number(tipCtx?.dataset?.tipX) || 0;
  const tip2 = Number(tipCtx?.dataset?.tipTwo) || 0;

  var tipPieChart = new Chart(tipCtx.getContext('2d'), {
    type: 'pie',
    data: {
      labels: [
        '1 ' + safePercent(tip1, total),
        'X ' + safePercent(tipX, total),
        '2 ' + safePercent(tip2, total),
      ],
      datasets: [
        {
          data: [tip1, tipX, tip2],
          backgroundColor: ['#46BFBD', '#FDB45C', '#F7464A'],
          hoverBackgroundColor: ['#5AD3D1', '#FFC870', '#FF5A5E'],
        },
      ],
    },
    options: { responsive: true },
  });

  const roundsCtx = document.getElementById(`${userId}-round-stats`);
  let roundStats = {};
  try {
    const raw = roundsCtx?.dataset?.stats || '{}';
    roundStats = typeof raw === 'string' ? JSON.parse(raw) : raw;
  } catch (err) {
    console.warn('Invalid round_stats JSON for user', userId, err);
    roundStats = {};
  }

  const roundScores = [];
  const roundGuesses = [];
  for (let i = 1; i <= 38; i++) {
    const key = String(i);
    if (roundStats[key]) {
      roundScores.push(Number(roundStats[key].correct) || 0);
      roundGuesses.push(Number(roundStats[key].tips) || 0);
    } else {
      roundScores.push(0);
      roundGuesses.push(0);
    }
  }

  var roundStatChart = new Chart(roundsCtx.getContext('2d'), {
    type: 'line',
    data: {
      labels: range(1, 38),
      datasets: [
        {
          label: 'Antal rätt',
          data: roundScores,
          backgroundColor: 'rgba(105,0,132,.2)',
          borderColor: 'rgba(200,99,132,.7)',
          borderWidth: 2,
          lineTension: 0,
        },
        {
          label: 'Tips Gjorda',
          data: roundGuesses,
          backgroundColor: 'rgba(2,0,132,.2)',
          borderColor: 'rgba(2,99,132,.7)',
          borderWidth: 2,
          lineTension: 0,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        yAxes: [{ display: true, ticks: { beginAtZero: true } }],
      },
    },
  });
}

function range(start, end) {
  return Array(end - start + 1)
    .fill()
    .map((_, idx) => start + idx);
}

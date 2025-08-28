var carousels = document.getElementsByClassName('carousel');

for (const carousel of carousels) {
  const userId = carousel.dataset.userId;
  const total = carousel.dataset.total;

  const correctCtx = document.getElementById(`${userId}-correct-chart`);
  const correct = correctCtx.dataset.correct;
  const incorrect = correctCtx.dataset.incorrect;
  const notPlayed = total - correctCtx.dataset.finished;

  var correctPieChart = new Chart(correctCtx.getContext('2d'), {
    type: 'pie',
    data: {
      labels: [
        'Antal rätt ' + percentage(correct, total),
        'Antal fel ' + percentage(incorrect, total),
        'Ej spelade ' + percentage(notPlayed, total),
      ],
      datasets: [
        {
          data: [correct, incorrect, notPlayed],
          backgroundColor: ['#46BFBD', '#F7464A', '#FDB45C'],
          hoverBackgroundColor: ['#5AD3D1', '#FF5A5E', '#FFC870'],
        },
      ],
    },
    options: {
      responsive: true,
    },
  });

  const tipCtx = document.getElementById(`${userId}-tip-chart`);
  const tip1 = tipCtx.dataset.tipOne;
  const tipX = tipCtx.dataset.tipX;
  const tip2 = tipCtx.dataset.tipTwo;

  var tipPieChart = new Chart(tipCtx.getContext('2d'), {
    type: 'pie',
    data: {
      labels: [
        '1 ' + percentage(tip1, total),
        'X ' + percentage(tipX, total),
        '2 ' + percentage(tip2, total),
      ],
      datasets: [
        {
          data: [tip1, tipX, tip2],
          backgroundColor: ['#46BFBD', '#FDB45C', '#F7464A'],
          hoverBackgroundColor: ['#5AD3D1', '#FFC870', '#FF5A5E'],
        },
      ],
    },
    options: {
      responsive: true,
    },
  });

  const roundsCtx = document.getElementById(`${userId}-round-stats`);
  const roundStats = JSON.parse(roundsCtx.dataset.stats);
  const roundScores = [];
  const roundGuesses = [];
  for (let i = 1; i <= 38; i++) {
    const round = String(i);
    if (roundStats[round]) {
      roundScores.push(roundStats[round].correct);
      roundGuesses.push(roundStats[round].tips);
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
          backgroundColor: 'rgba(105, 0, 132, .2)',
          borderColor: 'rgba(200, 99, 132, .7)',
          borderWidth: 2,
          lineTension: 0,
        },
        {
          label: 'Tips Gjorda',
          data: roundGuesses,
          backgroundColor: 'rgba(2, 0, 132, .2)',
          borderColor: 'rgba(2, 99, 132, .7)',
          borderWidth: 2,
          lineTension: 0,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        yAxes: [
          {
            display: true,
            ticks: {
              beginAtZero: true,
              steps: 10,
              stepValue: 1,
              max: 10,
            },
          },
        ],
      },
    },
  });
}

function range(start, end) {
  return Array(end - start + 1)
    .fill()
    .map((_, idx) => start + idx);
}

function percentage(partialValue, totalValue) {
  return Math.round((100 * partialValue) / totalValue) + '%';
}

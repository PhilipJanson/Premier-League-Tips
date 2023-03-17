var carousels = document.getElementsByClassName('carousel');

for (const carousel of carousels) {
  var userId = carousel.dataset.userId;
  var total = carousel.dataset.total;

  var correctCtx = document.getElementById(`${userId}-correct-chart`);
  var correct = correctCtx.dataset.correct;
  var incorrect = correctCtx.dataset.incorrect;

  var correctPieChart = new Chart(correctCtx.getContext('2d'), {
    type: 'pie',
    data: {
      labels: [
        'Antal rätt ' + percentage(correct, total),
        'Antal fel ' + percentage(incorrect, total),
      ],
      datasets: [
        {
          data: [correct, incorrect],
          backgroundColor: ['#46BFBD', '#F7464A'],
          hoverBackgroundColor: ['#5AD3D1', '#FF5A5E'],
        },
      ],
    },
    options: {
      responsive: true,
    },
  });

  var tipCtx = document.getElementById(`${userId}-tip-chart`);
  var tip1 = tipCtx.dataset.tipOne;
  var tipX = tipCtx.dataset.tipX;
  var tip2 = tipCtx.dataset.tipTwo;

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

  var roundsCtx = document.getElementById(`${userId}-round-scores`);
  var roundScores = roundsCtx.dataset.rounds;

  var roundScoreChart = new Chart(roundsCtx.getContext('2d'), {
    type: 'line',
    data: {
      labels: range(1, 38),
      datasets: [
        {
          label: 'Antal rätt',
          data: roundScores.split('-'),
          backgroundColor: 'rgba(105, 0, 132, .2)',
          borderColor: 'rgba(200, 99, 132, .7)',
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

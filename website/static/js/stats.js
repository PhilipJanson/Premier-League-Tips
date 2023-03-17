var username = 'philip';
var total = document.getElementById(`${username}-total`).innerText.trim();

var correctCtx = document.getElementById('correct-chart').getContext('2d');
var correct = document.getElementById(`${username}-correct`).innerText.trim();
var incorrect = document
  .getElementById(`${username}-incorrect`)
  .innerText.trim();

var correctPieChart = new Chart(correctCtx, {
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

var tipCtx = document.getElementById('tip-chart').getContext('2d');
var tip1 = document.getElementById(`${username}-tip-1`).innerText.trim();
var tipX = document.getElementById(`${username}-tip-X`).innerText.trim();
var tip2 = document.getElementById(`${username}-tip-2`).innerText.trim();

var tipPieChart = new Chart(tipCtx, {
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

var roundsCtx = document.getElementById('round-scores').getContext('2d');
var roundScores = document
  .getElementById(`${username}-round-scores`)
  .innerText.trim();

var roundScoreChart = new Chart(roundsCtx, {
  type: 'line',
  data: {
    labels: range(1, 38),
    datasets: [
      {
        label: 'Antal rätt per omgång',
        data: roundScores.split('-'),
        backgroundColor: 'rgba(105, 0, 132, .2)',
        borderColor: 'rgba(200, 99, 132, .7)',
        borderWidth: 2,
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

function range(start, end) {
  return Array(end - start + 1)
    .fill()
    .map((_, idx) => start + idx);
}

function percentage(partialValue, totalValue) {
  return Math.round((100 * partialValue) / totalValue) + '%';
}

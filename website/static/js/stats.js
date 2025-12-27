const ROUNDS = 38;

document.addEventListener('DOMContentLoaded', () => {
  function range(start, end) {
    return Array.from({ length: end - start + 1 }, (_, i) => start + i);
  }

  function safePercent(part, total) {
    if (!total || total === 0) return '0%';
    return Math.round((100 * part) / total) + '%';
  }

  function parseRoundStats(canvas, dataId) {
    try {
      const raw = canvas.getAttribute(dataId) || '{}';
      return JSON.parse(raw);
    } catch (err) {
      console.warn('Invalid data-round-stats JSON for canvas', canvas.id, err);
      return {};
    }
  }

  document.querySelectorAll('.pie-chart').forEach((canvas) => {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const total = Number(canvas.dataset.total) || 0;
    if (canvas.id.includes('correct-chart')) {
      const correct = Number(canvas.dataset.correct) || 0;
      const incorrect = Number(canvas.dataset.incorrect) || 0;
      const finished = Number(canvas.dataset.finished) || 0;
      const notPlayed = Math.max(0, total - finished);

      new Chart(ctx, {
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
    }

    if (canvas.id.includes('tip-chart')) {
      const tip1 = Number(canvas.dataset.tipOne) || 0;
      const tipX = Number(canvas.dataset.tipX) || 0;
      const tip2 = Number(canvas.dataset.tipTwo) || 0;

      new Chart(ctx, {
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
    }
  });

  document.querySelectorAll('.line-graph').forEach((canvas) => {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const roundStats = parseRoundStats(canvas, 'data-round-stats');
    const compareStats = parseRoundStats(canvas, 'data-compare-round-stats');

    const roundScores = [];
    const compareRoundScores = [];
    const roundGuesses = [];
    for (let i = 1; i <= ROUNDS; i++) {
      const currRound = String(i);
      if (roundStats[currRound]) {
        roundScores.push(Number(roundStats[currRound].correct) || 0);
        roundGuesses.push(Number(roundStats[currRound].tips) || 0);
      } else {
        roundScores.push(0);
        roundGuesses.push(0);
      }
      if (compareStats[currRound]) {
        compareRoundScores.push(Number(compareStats[currRound].correct) || 0);
      } else {
        compareRoundScores.push(0);
      }
    }

    let datasets = [];
    if (compareStats && Object.keys(compareStats).length === 0) {
      datasets = [
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
      ];
    } else {
      datasets = [
        {
          label: 'Antal rätt ' + canvas.dataset.user,
          data: roundScores,
          backgroundColor: 'rgba(0, 189, 57, 0.2)',
          borderColor: 'rgba(0, 92, 29, 0.2)',
          borderWidth: 2,
          lineTension: 0,
        },
        {
          label: 'Antal rätt ' + canvas.dataset.compareUser,
          data: compareRoundScores,
          backgroundColor: 'rgba(241, 57, 57, 0.2)',
          borderColor: 'rgba(138, 31, 31, 0.7)',
          borderWidth: 2,
          lineTension: 0,
        },
      ];
    }

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: range(1, ROUNDS),
        datasets: datasets,
      },
      options: {
        responsive: true,
        scales: {
          yAxes: [
            { display: true, ticks: { beginAtZero: true, min: 0, max: 10 } },
          ],
        },
      },
    });
  });

  document.querySelectorAll('.compare-user-form').forEach((select) => {
    select.addEventListener('change', async (e) => {
      const userId = e.target.value;
      const url = new URL(window.location.href);

      if (userId !== '') {
        url.searchParams.set('compareTo', userId);
      } else {
        url.searchParams.delete('compareTo');
      }

      window.location.href = url.toString();
    });
  });
});

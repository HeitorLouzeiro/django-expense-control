const renderChart = (labels, data) => {
  const ctx = document.getElementById('myChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Expense',
          data: data,
        },
      ],
    },
    options: {
      layout: {
        padding: 1,
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
};

const getChartData = () => {
  fetch("stats/expense-category-line-summary/")
    .then((res) => res.json())
    .then((results) => {
      const labels = results.labels;
      const data = results.data;
      renderChart(labels, data);
    })
    .catch((error) => console.error("Error fetching data:", error));
};

document.addEventListener("DOMContentLoaded", getChartData);

const renderChart2 = (data, labels) => {
  const ctx2 = document.getElementById("myChart2");

  new Chart(ctx2, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Last 6 months expenses",
          data: data,
          borderWidth: 1,
        },
      ],
    },
    options: {
      plugins: {
        title: {
          display: true,
          text: "Categories",
        },
      },
    },
  });
};

const getChatData2 = () => {
    fetch("stats/expense-category-summary/")
        .then((res) => res.json())
        .then((results) => {
            // console.log("results", results);
            const category_data = results.expense_category_data;
            const labels = Object.keys(category_data);
            const data = Object.values(category_data);
            renderChart2(data, labels); // Pass data and labels directly
        });
};

document.onload = getChatData2();
const renderChart = (data, labels) => {
    const ctx = document.getElementById("myChart");
  
    new Chart(ctx, {
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
            text: "Custom Chart Title",
          },
        },
      },
    });
  };
  
  const getChatData = () => {
      fetch("expense-category-summary/")
          .then((res) => res.json())
          .then((results) => {
              // console.log("results", results);
              const category_data = results.expense_category_data;
              const labels = Object.keys(category_data);
              const data = Object.values(category_data);
              renderChart(data, labels); // Pass data and labels directly
          });
  };
  
  document.onload = getChatData();
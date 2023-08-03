const searchField = document.querySelector("#searchField");

const tableOutput = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const paginationContainer = document.querySelector(".pagination-container");
const tbody = document.querySelector(".table-body");

tableOutput.style.display = "none";

searchField.addEventListener("keyup", (e) => {
  const searchValue = e.target.value;

  if (searchValue.trim().length > 0) {
    paginationContainer.style.display = "none";
    // console.log("searchValue", searchValue);
    fetch("search-expenses/", {
      body: JSON.stringify({ searchText: searchValue }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("data", data);
        appTable.style.display = "none";

        tableOutput.style.display = "block";

        if (data.length === 0) {
          tbody.innerHTML = "<tr><td colspan='5'>No result found</td></tr>";
        } else {
          const promises = data.map((item) =>
            fetch(`get-category/${item.category_id}/`).then((res) => res.json())
          );
          Promise.all(promises).then((categories) => {
            let tableRows = "";

            data.forEach((item, index) => {
              const category = categories[index];
              tableRows += `
                            <tr>
                              <td>${item.amount}</td>
                              <td>${category.name}</td>
                              <td>${item.description}</td>
                              <td>${item.date}</td>
                              <td>
                                <a href="edit/expense/${item.id}" class="btn btn-primary btn-sm">Edit</a>
                                <a href="delete/expense/${item.id}" class="btn btn-danger btn-sm">Delete</a>
                              </td>
                            </tr>`;
            });
            tbody.innerHTML = tableRows;
          });
        }
      });
  } else {
    appTable.style.display = "block";
    paginationContainer.style.display = "block";
    tableOutput.style.display = "none";
    tbody.innerHTML = "";
  }
});

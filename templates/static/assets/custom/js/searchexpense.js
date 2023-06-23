const searchField = document.querySelector("#searchField");

const tableOutput = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const paginationContainer = document.querySelector(".pagination-container");
const tbody = document.querySelector(".table-body");

tableOutput.style.display = "none";


searchField.addEventListener("keyup", (e) => {
    const searchValue = e.target.value;

    if(searchValue.trim().length > 0){
        paginationContainer.style.display = "none";
        console.log("searchValue", searchValue);
        tbody.innerHTML = "";
        fetch("search-expenses/", {
            body: JSON.stringify({ searchText: searchValue }),
            method: "POST",
        })
        .then((res) => res.json())
        .then((data) => {
            console.log("data", data);
            appTable.style.display = "none";

            tableOutput.style.display = "block";

            if(data.length === 0){
                tableOutput.innerHTML = "No result found";
            }else{
                data.forEach((item) => {
                    // Fazer uma nova solicitação para obter as informações da categoria
                    fetch(`get-category/${item.category_id}/`)
                      .then((res) => res.json())
                      .then((category) => {
                        tbody.innerHTML += `
                            <tr>
                              <td>${item.amount}</td>
                              <td>${category.name}</td>
                              <td>${item.description}</td>
                              <td>${item.date}</td>
                            </tr>`;
                      });
                  });
                }
              });
    }else{
        appTable.style.display = "block";
        paginationContainer.style.display = "block";
        tableOutput.style.display = "none";
    }
});
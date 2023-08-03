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
    // console.log("searchValue", searchValue);
    fetch("search-incomes/", {
      body: JSON.stringify({ searchText: searchValue }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("data", data);
        appTable.style.display = "none";

        tableOutput.style.display = "block";

        if (data.length === 0) {
          // Se não houver resultados, exibir mensagem
          tbody.innerHTML = "<tr><td colspan='5'>No result found</td></tr>";
        } else {
          // Criar um array de promessas para carregar as informações da categoria para cada resultado
          const promises = data.map((item) =>
            fetch(`get-source/${item.source_id}/`).then((res) => res.json())
          );

          // Aguardar todas as promessas serem resolvidas
          Promise.all(promises).then((sources) => {
            let tableRows = "";

            data.forEach((item, index) => {
              const source = sources[index];
              tableRows += `
                <tr>
                  <td>${item.amount}</td>
                  <td>${source.name}</td>
                  <td>${item.description}</td>
                  <td>${item.date}</td>
                  <td>
                    <a href="edit/income/${item.id}/" class="btn btn-primary btn-sm">Edit</a>
                    <a href="delete/income/${item.id}/" class="btn btn-danger btn-sm">Delete</a>
                  </td>
                </tr>`;
            });

            // Definir o conteúdo da tabela com todas as linhas
            tbody.innerHTML = tableRows;
          });
        }
      });
  } else {
    appTable.style.display = "block";
    paginationContainer.style.display = "block";
    tableOutput.style.display = "none";
    tbody.innerHTML = ""; // Limpar o conteúdo no caso de pesquisa vazia
  }
});
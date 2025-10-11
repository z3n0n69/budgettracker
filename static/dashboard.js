function getusername() {
    // Find the cookie that starts with "username="
    let username = document.cookie
        .split("; ")
        .find(row => row.startsWith("username="))
        ?.split("=")[1];

    // If username exists, display it, otherwise show "Guest"
    document.getElementById("displayusername").innerHTML = username || "Guest";
}

getusername();



document.addEventListener("DOMContentLoaded", function () {
  const select = document.getElementById("addremoveSelect");
  const descriptionInput = document.getElementById("descriptionInput");
  const amountInput = document.getElementById("amountInput");

  select.addEventListener("change", function () {
    if (this.value === "remove") {
      // Change description input to transaction_id
      descriptionInput.placeholder = "Transaction ID";
      descriptionInput.type = "number";
      descriptionInput.name = "transactionID"; 


      // Remove the amount input
      amountInput.style.display = "none";
      amountInput.removeAttribute("required");
    } else {
      // Restore to Add mode
      descriptionInput.placeholder = "Expense description";
      descriptionInput.type = "text"; 
      descriptionInput.name = "expenseDescription"

      amountInput.style.display = "inline-block";
      amountInput.setAttribute("required", "true");
      
    }
  });
});

function get_expenses() {
  fetch("/fetch_expenses")
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById("expenseDisplay");
      container.innerHTML = ""; // clear old content

      data.forEach(item => {
        // create a new element for each expense
        const div = document.createElement("div");
        div.textContent = `${item.transaction_ID} | ${item.username} | ${item.transaction_name} | ₱${item.amount}`;
        container.appendChild(div);
      });
    })
}
get_expenses(); 

function get_money() {
  fetch("/fetch_balance")
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById("currentbalance");

      data.forEach(item => {
        // change value in the current balance
        container.innerHTML = item.money; 
      });
    })
}

get_money(); 

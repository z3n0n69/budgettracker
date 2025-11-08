function get_schedule(){
    fetch("/fetch_schedule")

    .then(response => response.json())
    .then(data => {
        const container = document.getElementById("scheduleList")
        container.innerHTML = ""
        data.forEach(item => {
            const list = document.createElement("li"); 
            list.textContent = `${item.scheduleID} | ${item.schedule_name} | $${item.schedule_amount} | ${item.schedule_date}`; 
            container.appendChild(list)
        }); 
    })
}

get_schedule(); 



document.addEventListener("DOMContentLoaded", function () {
  const select = document.getElementById("scheduletype");
  const months = document.getElementById("months");
  const container = document.getElementById("multischedulediv"); 
  const input = document.createElement("input"); 
  select.addEventListener("change", function () {
    if (this.value === "semimonthly") {
      // Change description input to transaction_id
      months.placeholder = "select end date";
      months.type = "date";
      months.name = "enddate"; 

      input.name = "months"; 
      input.type = "number"; 
      input.placeholder = "Months"; 
      container.appendChild(input)


     
    } else {
      // Restore to Add mode
      months.type = "number"; 
      months.name = "months"
      months.placeholder = "Months"; 
      container.removeChild(input)
      
    }
  });
});
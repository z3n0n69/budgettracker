function get_schedule(){
    fetch("/fetch_schedule")

    .then(response => response.json())
    .then(data => {
        const container = document.getElementById("scheduleList")

        data.forEach(item => {
            const list = document.createElement("li"); 
            list.textContent = `${item.schedule_name} | $${item.schedule_amount} | ${item.schedule_date}`; 
            container.appendChild(list)
        }); 
    })
}

get_schedule(); 
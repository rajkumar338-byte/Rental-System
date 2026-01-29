function loadData(url, tableId, isReport = false) {
    fetch(url)
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector(`#${tableId} tbody`);
            tbody.innerHTML = "";
            data.forEach(row => {
                let tr = "<tr>";
                // Report now shows 5 text columns (Prop Name, Contact, Price, Cust Name, Billing Date)
                let displayLimit = isReport ? 5 : row.length;

                for (let i = 0; i < displayLimit; i++) {
                    if (!isReport && i === 4) { 
                        const style = row[i] === 'Rented' ? 'rented' : 'available';
                        tr += `<td class="${style}">${row[i]}</td>`;
                    } else {
                        tr += `<td>${row[i]}</td>`;
                    }
                }

                if (tableId === "propTable") {
                    tr += `<td><a href="/edit_property.html?id=${row[0]}" class="edit-btn">Edit</a></td>`;
                } else if (tableId === "reportTable") {
                    // row[5] is now the hidden Customer ID used for the View function
                    tr += `<td><button onclick="showDetails(${row[5]})" class="edit-btn" style="background:#27ae60;">View</button></td>`;
                }
                tr += "</tr>";
                tbody.innerHTML += tr;
            });
        });
}

function showDetails(customerId) {
    fetch(`/api/get_rental_details?id=${customerId}`)
        .then(res => res.json())
        .then(data => {
            if (data.length > 0) {
                const d = data[0];
                const details = `
--- CUSTOMER DETAILS ---
Name: ${d[0]}
Contact: ${d[1]}
Billing Date: ${d[6]}

--- PROPERTY DETAILS ---
Property Name: ${d[2]}
Rent Price: ${d[3]}
Description: ${d[4]}
Status: ${d[5]}
                `;
                alert(details);
            }
        });
}
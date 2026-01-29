function loadData(url, tableId, isReport = false) {
    fetch(url)
        .then(res => {
            if (!res.ok) throw new Error('API Error');
            return res.json();
        })
        .then(data => {
            const tbody = document.querySelector(`#${tableId} tbody`);
            tbody.innerHTML = "";
            data.forEach(row => {
                let tr = "<tr>";
                // Report displays 5 columns (index 0-4), Property List displays all
                let displayLimit = isReport ? 5 : row.length;

                for (let i = 0; i < displayLimit; i++) {
                    if (!isReport && i === 4) { 
                        const style = row[i] === 'Rented' ? 'rented' : 'available';
                        tr += `<td class="${style}">${row[i]}</td>`;
                    } else {
                        tr += `<td>${row[i] || "N/A"}</td>`;
                    }
                }

                if (tableId === "propTable") {
                    tr += `<td><a href="/edit_property.html?id=${row[0]}" class="edit-btn">Edit</a></td>`;
                } else if (tableId === "reportTable") {
                    // FIX: row[5] is the Customer ID from the SQL query
                    tr += `<td><button onclick="showDetails(${row[5]})" class="edit-btn" style="background:#27ae60;">View</button></td>`;
                }
                tr += "</tr>";
                tbody.innerHTML += tr;
            });
        })
        .catch(err => console.error("Load Error:", err));
}

function showDetails(customerId) {
    if (!customerId) return alert("Error: ID is missing.");
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
Property: ${d[2]}
Price: ${d[3]}
Desc: ${d[4]}
Status: ${d[5]}
                `;
                alert(details);
            }
        });
}
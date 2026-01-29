function loadData(url, tableId, isReport = false) {
    fetch(url)
        .then(res => {
            if (!res.ok) throw new Error('API Error ' + res.status);
            return res.json();
        })
        .then(data => {
            const tbody = document.querySelector(`#${tableId} tbody`);
            tbody.innerHTML = "";
            data.forEach(row => {
                let tr = "<tr>";
                // Report shows 5 text columns (index 0,1,2,3,4)
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
                    // Navigate to rental details page instead of alert
                    tr += `<td><a href="/rental_details.html?id=${row[5]}" class="edit-btn" style="background:linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);">View</a></td>`;
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
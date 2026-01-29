function loadData(url, tableId, isReport = false) {
    fetch(url)
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector(`#${tableId} tbody`);
            tbody.innerHTML = "";
            data.forEach(row => {
                let tr = "<tr>";
                
                // For Report, display only the first 4 columns (Name, Contact, Price, Customer)
                // The 5th column (row[4]) is the ID used for the button
                let displayLimit = isReport ? 4 : row.length;

                for (let i = 0; i < displayLimit; i++) {
                    if (!isReport && i === 4) { // Status column color logic
                        const style = row[i] === 'Rented' ? 'rented' : 'available';
                        tr += `<td class="${style}">${row[i]}</td>`;
                    } else {
                        tr += `<td>${row[i]}</td>`;
                    }
                }

                // Action Column Logic
                if (tableId === "propTable") {
                    // row[0] is the Property ID from the DB
                    tr += `<td><a href="/edit_property.html?id=${row[0]}" class="edit-btn">Edit</a></td>`;
                } else if (tableId === "reportTable") {
                    // row[4] is the Customer ID added to the JOIN query in app.py
                    tr += `<td><button onclick="alert('Viewing Customer ID: ' + ${row[4]})" class="edit-btn" style="background:#27ae60; border:none; color:white; padding:5px 10px; cursor:pointer; border-radius:4px;">View</button></td>`;
                }

                tr += "</tr>";
                tbody.innerHTML += tr;
            });
        });
}
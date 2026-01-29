function loadData(url, tableId, isReport = false) {
    fetch(url)
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector(`#${tableId} tbody`);
            tbody.innerHTML = "";
            data.forEach(row => {
                let tr = "<tr>";
                
                // Determine how many columns to show in the table
                // Report has 5 items (index 0-4), but we only display the first 4 as text
                let displayCount = isReport ? 4 : row.length;

                for (let i = 0; i < displayCount; i++) {
                    if (!isReport && i === 4) {
                        const style = row[i] === 'Rented' ? 'rented' : 'available';
                        tr += `<td class="${style}">${row[i]}</td>`;
                    } else {
                        tr += `<td>${row[i]}</td>`;
                    }
                }

                // Add Action Buttons
                if (tableId === "propTable") {
                    // row[0] is the Property ID
                    tr += `<td><a href="/edit_property.html?id=${row[0]}" class="edit-btn">Edit</a></td>`;
                } else if (tableId === "reportTable") {
                    // FIX: row[4] is the Customer ID from the JOIN query in app.py
                    tr += `<td><button onclick="alert('Viewing Customer ID: ' + ${row[4]})" class="edit-btn" style="background:#27ae60; border:none; color:white; padding:5px 10px; cursor:pointer; border-radius:4px;">View</button></td>`;
                }

                tr += "</tr>";
                tbody.innerHTML += tr;
            });
        });
}
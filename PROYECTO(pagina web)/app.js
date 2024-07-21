console.log('app.js cargado correctamente');
document.getElementById('selectButton').addEventListener('click', () => {
    document.getElementById('pdfFileInput').click();
});

document.getElementById('pdfFileInput').addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        document.getElementById('processButton').disabled = false;
    }
});

document.getElementById('processButton').addEventListener('click', () => {
    const fileInput = document.getElementById('pdfFileInput');
    const file = fileInput.files[0];
    if (!file) {
        alert('Por favor, seleccione un archivo PDF primero.');
        return;
    }

    const formData = new FormData();
    formData.append('pdf', file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/process_pdf', true);

    xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            document.getElementById('progressBar').value = percentComplete;
        }
    };

    xhr.onload = () => {
        if (xhr.status === 200) {
            alert('El PDF ha sido procesado exitosamente.');
        } else {
            alert('Hubo un error al procesar el PDF.');
        }
    };

    xhr.send(formData);
});

document.getElementById('viewDataButton').addEventListener('click', () => {
    fetch('/view_data')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#dataTable tbody');
            tableBody.innerHTML = '';
            data.forEach(row => {
                const tr = document.createElement('tr');
                Object.values(row).forEach(cellData => {
                    const td = document.createElement('td');
                    td.textContent = cellData;
                    tr.appendChild(td);
                });
                tableBody.appendChild(tr);
            });
        });
});

document.getElementById('addAnotherButton').addEventListener('click', () => {
    const exit = confirm('¿Desea salir?');
    if (!exit) {
        document.getElementById('pdfFileInput').value = '';
        document.getElementById('processButton').disabled = true;
    } else {
        window.close();
    }
});

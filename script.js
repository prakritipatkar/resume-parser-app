document.getElementById('resumeFile').addEventListener('change', function () {
    const file = this.files[0];
    const resultDiv = document.getElementById('result');
    const loader = document.getElementById('loader');

    if (file) {
        resultDiv.innerText = '';
        loader.style.display = 'block';

        const formData = new FormData();
        formData.append('resume', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loader.style.display = 'none';
            resultDiv.innerHTML = `<h3>Parsed Resume Data:</h3>`;
            for (const [key, value] of Object.entries(data)) {
                resultDiv.innerHTML += `<p><strong>${key}:</strong> ${value}</p>`;
            }
        })
        .catch(error => {
            loader.style.display = 'none';
            console.error('Error:', error);
            resultDiv.innerText = 'Error uploading file.';
        });
    }
});

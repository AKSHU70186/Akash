document.getElementById('scrapeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const errorDiv = document.getElementById('error');
    const resultsJson = document.getElementById('resultsJson');
    const submitButton = form.querySelector('button');
    
    try {
        // Show loading state
        submitButton.disabled = true;
        loadingDiv.classList.remove('hidden');
        resultsDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        
        const formData = new FormData(form);
        
        const response = await fetch('/scrape', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Show results
            resultsDiv.classList.remove('hidden');
            resultsJson.textContent = JSON.stringify(data, null, 2);
        } else {
            // Show error
            errorDiv.classList.remove('hidden');
            document.getElementById('errorMessage').textContent = data.message || 'An error occurred';
        }
    } catch (error) {
        // Show error
        errorDiv.classList.remove('hidden');
        document.getElementById('errorMessage').textContent = 
            'Failed to connect to the server. Please try again.';
    } finally {
        // Reset states
        loadingDiv.classList.add('hidden');
        submitButton.disabled = false;
    }
}); 
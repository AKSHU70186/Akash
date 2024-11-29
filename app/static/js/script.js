document.getElementById('scrapeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const errorDiv = document.getElementById('error');
    const resultsJson = document.getElementById('resultsJson');
    const resultsContainer = document.getElementById('resultsContainer');
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
            
            // Clear previous results
            resultsContainer.innerHTML = '';
            
            // Display news articles in a grid
            if (formData.get('scraper_type') === 'news' && data.data.scraped_data.length > 0) {
                data.data.scraped_data.forEach(article => {
                    const articleElement = document.createElement('div');
                    articleElement.className = 'bg-white rounded-lg shadow-md p-4';
                    articleElement.innerHTML = `
                        ${article.image_url ? `<img src="${article.image_url}" alt="${article.title}" class="w-full h-48 object-cover rounded-t-lg">` : ''}
                        <h3 class="text-lg font-semibold mt-2">${article.title}</h3>
                        ${article.excerpt ? `<p class="text-gray-600 mt-2">${article.excerpt}</p>` : ''}
                        ${article.date ? `<p class="text-gray-500 text-sm mt-2">${article.date}</p>` : ''}
                        ${article.link ? `<a href="${article.link}" target="_blank" class="text-blue-600 hover:text-blue-800 mt-2 inline-block">Read more</a>` : ''}
                    `;
                    resultsContainer.appendChild(articleElement);
                });
            }
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
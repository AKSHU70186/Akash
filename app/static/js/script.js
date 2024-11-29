document.getElementById('preset-urls').addEventListener('change', function(e) {
    const urlInput = document.getElementById('url');
    urlInput.value = e.target.value;
});

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
            
            if (formData.get('scraper_type') === 'news' && data.data.scraped_data.length > 0) {
                data.data.scraped_data.forEach(article => {
                    displayArticle(article, resultsContainer);
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

function displayArticle(article, container) {
    const articleElement = document.createElement('div');
    articleElement.className = 'bg-white rounded-lg shadow-md p-4 mb-4';
    
    articleElement.innerHTML = `
        <div class="flex flex-col md:flex-row">
            ${article.image_url ? `
                <div class="md:w-1/3 mb-4 md:mb-0 md:mr-4">
                    <img src="${article.image_url}" alt="${article.title}" 
                         class="w-full h-48 object-cover rounded-lg">
                </div>
            ` : ''}
            <div class="md:${article.image_url ? 'w-2/3' : 'w-full'}">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="text-xl font-bold">
                        <a href="${article.link}" target="_blank" 
                           class="text-blue-600 hover:text-blue-800">
                            ${article.title}
                        </a>
                    </h3>
                    <span class="text-sm text-gray-500 ml-2">
                        ${article.source}
                    </span>
                </div>
                ${article.date ? `
                    <p class="text-gray-500 text-sm mb-2">
                        ${article.date}
                    </p>
                ` : ''}
                ${article.description ? `
                    <p class="text-gray-700 mb-4">
                        ${article.description}
                    </p>
                ` : ''}
                <a href="${article.link}" target="_blank" 
                   class="inline-block bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    Read More
                </a>
            </div>
        </div>
    `;
    
    container.appendChild(articleElement);
} 
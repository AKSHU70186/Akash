document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('scrapeForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const error = document.getElementById('error');
    const articlesList = document.getElementById('articlesList');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = document.getElementById('urlSelect').value;
        if (!url) {
            error.textContent = 'Please select a website';
            error.classList.remove('hidden');
            return;
        }

        // Reset UI
        loading.classList.remove('hidden');
        results.classList.add('hidden');
        error.classList.add('hidden');
        articlesList.innerHTML = '';

        try {
            const formData = new FormData();
            formData.append('url', url);

            const response = await fetch('/scrape', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.status === 'success') {
                if (data.data.scraped_data.length === 0) {
                    error.textContent = 'No articles found';
                    error.classList.remove('hidden');
                } else {
                    data.data.scraped_data.forEach(article => {
                        const articleElement = createArticleElement(article);
                        articlesList.appendChild(articleElement);
                    });
                    results.classList.remove('hidden');
                    document.getElementById('exportButtons').classList.remove('hidden');
                }
            } else {
                throw new Error(data.message || 'Failed to scrape data');
            }
        } catch (err) {
            error.textContent = err.message || 'An error occurred while scraping';
            error.classList.remove('hidden');
        } finally {
            loading.classList.add('hidden');
        }
    });
});

function createArticleElement(article) {
    const div = document.createElement('div');
    div.className = 'bg-white p-6 rounded-lg shadow-md';
    
    div.innerHTML = `
        <h3 class="text-xl font-bold mb-2">
            <a href="${article.link}" target="_blank" class="text-blue-600 hover:text-blue-800">
                ${article.title}
            </a>
        </h3>
        ${article.description ? `
            <p class="text-gray-600 mb-4">${article.description}</p>
        ` : ''}
        <div class="flex justify-between items-center text-sm text-gray-500">
            <span>${article.source}</span>
            ${article.date ? `<span>${article.date}</span>` : ''}
        </div>
    `;
    
    return div;
}

async function exportData(format) {
    try {
        const response = await fetch(`/export/${format}`, {
            method: 'GET',
        });

        if (!response.ok) {
            throw new Error('Export failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `news_data.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    } catch (err) {
        console.error('Export error:', err);
        error.textContent = 'Failed to export data';
        error.classList.remove('hidden');
    }
} 
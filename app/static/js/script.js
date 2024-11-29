document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('scrapeForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const error = document.getElementById('error');
    const contentList = document.getElementById('contentList');
    const exportButtons = document.getElementById('exportButtons');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = document.getElementById('url').value;
        if (!url) {
            showError('Please enter a valid URL');
            return;
        }

        // Reset UI
        resetUI();
        loading.classList.remove('hidden');

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
                    showError('No articles found on this page');
                } else {
                    displayResults(data.data.scraped_data);
                }
            } else {
                showError(data.message || 'Failed to scrape content');
            }
        } catch (err) {
            showError('An error occurred while scraping');
            console.error(err);
        } finally {
            loading.classList.add('hidden');
        }
    });
});

function resetUI() {
    loading.classList.add('hidden');
    results.classList.add('hidden');
    error.classList.add('hidden');
    contentList.innerHTML = '';
    exportButtons.classList.add('hidden');
}

function showError(message) {
    error.querySelector('p').textContent = message;
    error.classList.remove('hidden');
    error.classList.add('animate-fade-in');
}

function displayResults(items) {
    contentList.innerHTML = '';
    
    items.forEach((item, index) => {
        const article = document.createElement('div');
        article.className = 'bg-white rounded-lg shadow-md p-6 mb-4 article-card animate-slide-in';
        article.style.animationDelay = `${index * 0.1}s`;
        
        article.innerHTML = `
            <div class="space-y-4">
                <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-blue-600">
                        ${item.source}
                    </span>
                    ${item.published_date ? `
                        <span class="text-sm text-gray-500">
                            <i class="far fa-clock mr-1"></i>
                            ${item.published_date}
                        </span>
                    ` : ''}
                </div>
                
                <h3 class="text-xl font-semibold text-gray-900">
                    ${item.title}
                </h3>
                
                <p class="text-gray-600">
                    ${item.summary}
                </p>
                
                <div class="pt-4 border-t border-gray-200">
                    <a href="${item.link}" 
                       target="_blank" 
                       class="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium">
                        Read Full Article 
                        <svg class="ml-2 w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                    </a>
                </div>
            </div>
        `;
        
        contentList.appendChild(article);
    });

    results.classList.remove('hidden');
    exportButtons.classList.remove('hidden');
}

function setUrl(url) {
    document.getElementById('url').value = url;
}

async function exportData(format) {
    try {
        const response = await fetch(`/export/${format}`);
        if (!response.ok) throw new Error('Export failed');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `scraped_data.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    } catch (err) {
        showError('Failed to export data');
        console.error(err);
    }
}

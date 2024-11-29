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
        article.className = 'bg-white rounded-lg shadow-md overflow-hidden article-card animate-slide-in';
        article.style.animationDelay = `${index * 0.1}s`;
        
        article.innerHTML = `
            <div class="p-6">
                <h3 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                    ${item.title}
                </h3>
                ${item.description ? `
                    <p class="text-gray-600 mb-4 line-clamp-3">
                        ${item.description}
                    </p>
                ` : ''}
                <div class="flex items-center justify-between">
                    <a href="${item.link}" target="_blank" 
                       class="text-blue-600 hover:text-blue-800 font-medium text-sm">
                        Read More <i class="fas fa-arrow-right ml-1"></i>
                    </a>
                    ${item.date ? `
                        <span class="text-sm text-gray-500">
                            <i class="far fa-calendar-alt mr-1"></i> ${item.date}
                        </span>
                    ` : ''}
                </div>
            </div>
        `;
        
        contentList.appendChild(article);
    });

    results.classList.remove('hidden');
    results.classList.add('animate-fade-in');
    exportButtons.classList.remove('hidden');
    exportButtons.classList.add('animate-fade-in');
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
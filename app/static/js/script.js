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
                    showError('No content found on this page');
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
    error.textContent = message;
    error.classList.remove('hidden');
}

function displayResults(items) {
    items.forEach(item => {
        const element = createContentElement(item);
        contentList.appendChild(element);
    });
    results.classList.remove('hidden');
    exportButtons.classList.remove('hidden');
}

function createContentElement(item) {
    const div = document.createElement('div');
    div.className = 'bg-white shadow rounded-lg p-4';
    
    let html = '';
    
    if (item.title) {
        html += `<h3 class="text-lg font-semibold mb-2">${item.title}</h3>`;
    }
    
    if (item.link) {
        html += `<a href="${item.link}" target="_blank" class="text-blue-500 hover:text-blue-700 mb-2 block">View Original</a>`;
    }
    
    if (item.description) {
        html += `<p class="text-gray-600">${item.description}</p>`;
    }
    
    div.innerHTML = html;
    return div;
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
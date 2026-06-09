document.addEventListener('DOMContentLoaded', () => {
    // Detect whether we are on the homepage or in the reports/ subdirectory
    const path = window.location.pathname;
    const isSubdir = path.includes('/reports/') || path.endsWith('.html') && !path.endsWith('index.html') && path.includes('reports');
    
    // Set up paths correctly relative to current URL location
    const archiveJsonUrl = isSubdir ? 'archive.json' : 'reports/archive.json';
    const reportBaseUrl = isSubdir ? '' : 'reports/';
    const homeUrl = isSubdir ? '../index.html' : 'index.html';
    
    // Retrieve selector element
    const selectEl = document.getElementById('archive-select');
    if (!selectEl) return;
    
    // Fetch archive index JSON
    fetch(archiveJsonUrl)
        .then(response => {
            if (!response.ok) throw new Error('Archive not found');
            return response.json();
        })
        .then(data => {
            if (!Array.isArray(data) || data.length === 0) return;
            
            // Add a default placeholder or Latest link
            const latestOpt = document.createElement('option');
            latestOpt.value = homeUrl;
            latestOpt.textContent = '📰 Última Edición';
            selectEl.appendChild(latestOpt);
            
            // Populate select option for each archived date
            data.forEach(item => {
                const opt = document.createElement('option');
                opt.value = isSubdir ? `${item.date}.html` : `reports/${item.date}.html`;
                opt.textContent = `📅 ${item.date} (${translateTone(item.tone)})`;
                
                // Mark current report as selected
                const currentFileName = path.split('/').pop() || '';
                if (currentFileName === `${item.date}.html` || (currentFileName === 'index.html' || currentFileName === '') && item.latest) {
                    opt.selected = true;
                }
                
                selectEl.appendChild(opt);
            });
            
            // Handle navigation changes
            selectEl.addEventListener('change', (e) => {
                const targetUrl = e.target.value;
                if (targetUrl) {
                    window.location.href = targetUrl;
                }
            });
        })
        .catch(err => {
            console.warn('Failed to load report archive index:', err);
        });
        
    function translateTone(tone) {
        if (!tone) return '';
        const tones = {
            'Risk-on': 'Alza',
            'Risk-off': 'Baja',
            'Neutral': 'Lateral',
            'Mixed': 'Mixto'
        };
        return tones[tone] || tone;
    }
});

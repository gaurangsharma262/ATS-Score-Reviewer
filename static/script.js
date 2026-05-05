document.addEventListener('DOMContentLoaded', () => {
    // Toggle logic for input methods
    const radios = document.querySelectorAll('input[name="input_method"]');
    const uploadSection = document.getElementById('uploadSection');
    const pasteSection = document.getElementById('pasteSection');

    radios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'upload') {
                uploadSection.classList.add('active');
                pasteSection.classList.remove('active');
            } else {
                uploadSection.classList.remove('active');
                pasteSection.classList.add('active');
            }
        });
    });

    // File Input UI update
    const fileInput = document.getElementById('resumeFile');
    const fileInfo = document.querySelector('.file-info');
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileInfo.textContent = e.target.files[0].name;
            fileInfo.style.color = 'var(--primary)';
        } else {
            fileInfo.textContent = 'PDF, DOCX, TXT';
            fileInfo.style.color = 'var(--text-muted)';
        }
    });

    // Drag and Drop Effects
    const wrapper = document.querySelector('.file-upload-wrapper');
    wrapper.addEventListener('dragover', (e) => {
        e.preventDefault();
        wrapper.classList.add('dragover');
    });
    ['dragleave', 'drop'].forEach(evt => {
        wrapper.addEventListener(evt, () => wrapper.classList.remove('dragover'));
    });

    // Tabs logic
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(btn.dataset.target).classList.add('active');
        });
    });

    // Form Submission
    const form = document.getElementById('evaluationForm');
    const submitBtn = document.getElementById('submitBtn');
    const emptyState = document.querySelector('.empty-state');
    const resultsContent = document.querySelector('.results-content');
    
    // Result elements
    const scorePercentage = document.getElementById('scorePercentage');
    const circleSvg = document.querySelector('.circle');
    const profileSummary = document.getElementById('profileSummary');
    const matchedList = document.getElementById('matchedKeywordsList');
    const missingList = document.getElementById('missingKeywordsList');
    const recText = document.getElementById('recommendationText');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // UI Loading state
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/api/evaluate', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Something went wrong during evaluation.');
            }
            
            // Populate Results
            emptyState.classList.add('hidden');
            resultsContent.classList.remove('hidden');
            
            // 1. Score and Circle
            const matchScoreStr = data.Match_Percentage || '0%';
            scorePercentage.textContent = matchScoreStr;
            
            const numericScore = parseInt(matchScoreStr.replace('%', '')) || 0;
            // The stroke-dasharray works as: "value, 100". So if value is 85, it fills 85% of 100.
            circleSvg.setAttribute('stroke-dasharray', `${numericScore}, 100`);
            
            // Determine circle color
            let strokeColor = 'var(--success)';
            if (numericScore < 60) strokeColor = 'var(--danger)';
            else if (numericScore < 80) strokeColor = '#f59e0b'; // warning yellow
            circleSvg.style.stroke = strokeColor;
            
            // 2. Profile Summary
            profileSummary.textContent = data.Profile_Summary || 'No summary provided.';
            
            // 3. Keywords
            matchedList.innerHTML = '';
            const matched = data.Matching_Keywords || [];
            if(matched.length === 0) matchedList.innerHTML = '<li>None found</li>';
            matched.forEach(kw => {
                const li = document.createElement('li');
                li.textContent = kw;
                matchedList.appendChild(li);
            });
            
            missingList.innerHTML = '';
            const missing = data.Missing_Keywords || [];
            if(missing.length === 0) missingList.innerHTML = '<li>None found</li>';
            missing.forEach(kw => {
                const li = document.createElement('li');
                li.textContent = kw;
                missingList.appendChild(li);
            });
            
            // 4. Recommendation
            recText.textContent = data.Recommendation || 'No recommendation provided.';

        } catch (error) {
            alert(error.message);
        } finally {
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
        }
    });
});

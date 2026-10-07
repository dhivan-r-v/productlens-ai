// ProductLens AI — Frontend Logic

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const imageInput = document.getElementById('imageInput');
  const csvInput = document.getElementById('csvInput');
  const imagePlaceholder = document.getElementById('imagePlaceholder');
  const imagePreviewContainer = document.getElementById('imagePreviewContainer');
  const imagePreview = document.getElementById('imagePreview');
  const removeImageBtn = document.getElementById('removeImageBtn');

  const csvPlaceholder = document.getElementById('csvPlaceholder');
  const csvInfoContainer = document.getElementById('csvInfoContainer');
  const csvFileName = document.getElementById('csvFileName');
  const csvFileStatus = document.getElementById('csvFileStatus');
  const removeCsvBtn = document.getElementById('removeCsvBtn');

  const loadSampleBtn = document.getElementById('loadSampleBtn');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const alertBanner = document.getElementById('alertBanner');

  const loadingCard = document.getElementById('loadingCard');
  const resultsSection = document.getElementById('resultsSection');
  const resetBtn = document.getElementById('resetBtn');

  // Results elements
  const resultsProductTitle = document.getElementById('resultsProductTitle');
  const anchorImagePreview = document.getElementById('anchorImagePreview');
  const anchorProductText = document.getElementById('anchorProductText');
  const anchorDataBadge = document.getElementById('anchorDataBadge');

  const valTotalRevenue = document.getElementById('valTotalRevenue');
  const valTotalUnits = document.getElementById('valTotalUnits');
  const valAvgPrice = document.getElementById('valAvgPrice');
  const valTrajectory = document.getElementById('valTrajectory');
  const salesBulletsList = document.getElementById('salesBulletsList');
  const visualObsList = document.getElementById('visualObsList');
  const hypothesesList = document.getElementById('hypothesesList');
  const experimentsList = document.getElementById('experimentsList');

  // State
  let imageFile = null;
  let csvFile = null;
  let isUsingSample = false;

  // Banner helper
  function showAlert(msg, isError = true) {
    alertBanner.textContent = msg;
    alertBanner.className = isError ? 'alert-banner error' : 'alert-banner';
    alertBanner.classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function hideAlert() {
    alertBanner.classList.add('hidden');
    alertBanner.textContent = '';
  }

  function updateAnalyzeButtonState() {
    const isReady = (imageFile && csvFile) || isUsingSample;
    analyzeBtn.disabled = !isReady;
  }

  // Image Selection
  imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      showAlert('Please select a valid image file (PNG, JPG, or WEBP).');
      return;
    }

    imageFile = file;
    isUsingSample = false;
    hideAlert();

    const url = URL.createObjectURL(file);
    imagePreview.src = url;
    imagePlaceholder.classList.add('hidden');
    imagePreviewContainer.classList.remove('hidden');

    updateAnalyzeButtonState();
  });

  removeImageBtn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    imageFile = null;
    isUsingSample = false;
    imageInput.value = '';
    imagePreview.src = '';
    imagePreviewContainer.classList.add('hidden');
    imagePlaceholder.classList.remove('hidden');
    updateAnalyzeButtonState();
  });

  // CSV Selection
  csvInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.csv')) {
      showAlert('Please upload a comma-separated .csv file.');
      return;
    }

    csvFile = file;
    isUsingSample = false;
    hideAlert();

    csvFileName.textContent = file.name;
    csvFileStatus.textContent = `${(file.size / 1024).toFixed(1)} KB • Ready for analysis`;
    csvPlaceholder.classList.add('hidden');
    csvInfoContainer.classList.remove('hidden');

    updateAnalyzeButtonState();
  });

  removeCsvBtn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    csvFile = null;
    isUsingSample = false;
    csvInput.value = '';
    csvInfoContainer.classList.add('hidden');
    csvPlaceholder.classList.remove('hidden');
    updateAnalyzeButtonState();
  });

  // Load Sample Data
  loadSampleBtn.addEventListener('click', () => {
    hideAlert();
    isUsingSample = true;
    imageFile = null;
    csvFile = null;
    imageInput.value = '';
    csvInput.value = '';

    // Set sample image preview
    imagePreview.src = '/static/sample_data/sample_product.jpg';
    imagePlaceholder.classList.add('hidden');
    imagePreviewContainer.classList.remove('hidden');

    // Set sample CSV info
    csvFileName.textContent = 'sample_sales.csv';
    csvFileStatus.textContent = 'Pre-bundled demo data (8 weekly records)';
    csvPlaceholder.classList.add('hidden');
    csvInfoContainer.classList.remove('hidden');

    updateAnalyzeButtonState();
  });

  // Analyze Product
  analyzeBtn.addEventListener('click', async () => {
    if (analyzeBtn.disabled) return;
    hideAlert();

    // Prepare FormData
    const formData = new FormData();
    if (isUsingSample) {
      formData.append('use_sample', 'true');
    } else {
      if (!imageFile || !csvFile) {
        showAlert('Both a product image and a sales CSV are required before analyzing.');
        return;
      }
      formData.append('image', imageFile);
      formData.append('csv', csvFile);
      formData.append('use_sample', 'false');
    }

    // Show loading
    loadingCard.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    analyzeBtn.disabled = true;

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'An unexpected error occurred during analysis.');
      }

      renderResults(data);
    } catch (err) {
      showAlert(err.message);
    } finally {
      loadingCard.classList.add('hidden');
      updateAnalyzeButtonState();
    }
  });

  // Render Analysis Results
  function renderResults(data) {
    // Top anchor metadata
    resultsProductTitle.textContent = `Product: ${data.product_name}`;
    anchorProductText.textContent = data.product_name;
    anchorImagePreview.src = isUsingSample ? '/static/sample_data/sample_product.jpg' : imagePreview.src;
    anchorDataBadge.textContent = `${data.sales_trends.total_units_sold} Units Recorded`;

    // Card 1: Sales Trends
    valTotalRevenue.textContent = `$${data.sales_trends.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    valTotalUnits.textContent = data.sales_trends.total_units_sold.toLocaleString();
    valAvgPrice.textContent = `$${data.sales_trends.average_price.toFixed(2)}`;
    valTrajectory.textContent = data.sales_trends.overall_trend;

    salesBulletsList.innerHTML = '';
    (data.sales_trends.trend_bullets || []).forEach(bullet => {
      const li = document.createElement('li');
      li.textContent = bullet;
      salesBulletsList.appendChild(li);
    });

    // Card 2: Visual Observations
    visualObsList.innerHTML = '';
    (data.visual_observations || []).forEach(obs => {
      const li = document.createElement('li');
      li.textContent = obs;
      visualObsList.appendChild(li);
    });

    // Card 3: Cross-Modal Hypotheses
    hypothesesList.innerHTML = '';
    if (data.cross_modal_hypotheses && data.cross_modal_hypotheses.length > 0) {
      data.cross_modal_hypotheses.forEach(h => {
        const item = document.createElement('div');
        item.className = 'hypothesis-item';
        item.innerHTML = `
          <div class="hypothesis-title">${escapeHtml(h.hypothesis)}</div>
          <div class="hypothesis-meta">
            <div class="meta-field">
              <strong>Sales Evidence</strong>
              ${escapeHtml(h.supporting_data)}
            </div>
            <div class="meta-field">
              <strong>Visual Factor</strong>
              ${escapeHtml(h.visual_factor)}
            </div>
          </div>
        `;
        hypothesesList.appendChild(item);
      });
    } else {
      hypothesesList.innerHTML = '<p class="card-explainer">Cross-modal reasoning will be fully evaluated by Gemini in Slice 2.</p>';
    }

    // Card 4: Recommended Experiments
    experimentsList.innerHTML = '';
    if (data.recommended_experiments && data.recommended_experiments.length > 0) {
      data.recommended_experiments.forEach(exp => {
        const item = document.createElement('div');
        item.className = 'experiment-item';
        item.innerHTML = `
          <div class="experiment-title">⚡ ${escapeHtml(exp.action)}</div>
          <div class="experiment-details">
            <div class="meta-field">
              <strong>What to Test</strong>
              ${escapeHtml(exp.what_to_change)}
            </div>
            <div class="meta-field">
              <strong>Metric to Measure</strong>
              ${escapeHtml(exp.metric_to_measure)}
            </div>
          </div>
        `;
        experimentsList.appendChild(item);
      });
    } else {
      experimentsList.innerHTML = '<p class="card-explainer">Recommended experiments will be generated by Gemini in Slice 2.</p>';
    }

    // Show Results
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
  }

  // Reset Flow
  resetBtn.addEventListener('click', () => {
    imageFile = null;
    csvFile = null;
    isUsingSample = false;
    imageInput.value = '';
    csvInput.value = '';

    imagePreview.src = '';
    imagePreviewContainer.classList.add('hidden');
    imagePlaceholder.classList.remove('hidden');

    csvInfoContainer.classList.add('hidden');
    csvPlaceholder.classList.remove('hidden');

    hideAlert();
    resultsSection.classList.add('hidden');
    updateAnalyzeButtonState();

    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
});

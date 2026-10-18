// ProductLens AI — Frontend Logic

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const imageInput = document.getElementById('imageInput');
  const csvInput = document.getElementById('csvInput');
  const imageDropzone = document.getElementById('imageDropzone');
  const csvDropzone = document.getElementById('csvDropzone');
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

  const REQUIRED_CSV_HEADERS = ['date', 'product', 'price', 'units_sold', 'revenue'];

  // Banner helper
  function showAlert(msg, isError = true) {
    alertBanner.innerHTML = `
      <span>${escapeHtml(msg)}</span>
      <button type="button" class="btn-remove" id="closeAlertBtn" title="Dismiss" style="margin-left: 1rem;">&times;</button>
    `;
    alertBanner.className = isError ? 'alert-banner error' : 'alert-banner';
    alertBanner.classList.remove('hidden');

    const closeBtn = document.getElementById('closeAlertBtn');
    if (closeBtn) {
      closeBtn.addEventListener('click', hideAlert);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function hideAlert() {
    alertBanner.classList.add('hidden');
    alertBanner.innerHTML = '';
  }

  function updateAnalyzeButtonState() {
    const isReady = (imageFile !== null && csvFile !== null) || isUsingSample;
    analyzeBtn.disabled = !isReady;
  }

  // Handle Image File
  function handleImageFile(file) {
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      imageFile = null;
      imageInput.value = '';
      imagePreview.src = '';
      imagePreviewContainer.classList.add('hidden');
      imagePlaceholder.classList.remove('hidden');
      updateAnalyzeButtonState();
      showAlert('Invalid file type: Please select an image file (PNG, JPG, or WEBP).');
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
  }

  // Handle CSV File with client-side header validation
  async function handleCsvFile(file) {
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.csv')) {
      csvFile = null;
      csvInput.value = '';
      csvInfoContainer.classList.add('hidden');
      csvPlaceholder.classList.remove('hidden');
      updateAnalyzeButtonState();
      showAlert('Invalid file format: Please select a comma-separated .csv file.');
      return;
    }

    try {
      const text = await file.text();
      const firstLine = text.split(/\r?\n/)[0] || '';
      const headers = firstLine.split(',').map(h => h.trim().toLowerCase().replace(/\s+/g, '_'));

      const missing = REQUIRED_CSV_HEADERS.filter(req => !headers.includes(req));
      if (missing.length > 0) {
        csvFile = null;
        csvInput.value = '';
        csvInfoContainer.classList.add('hidden');
        csvPlaceholder.classList.remove('hidden');
        updateAnalyzeButtonState();
        showAlert(`Invalid CSV schema: Missing required columns: ${missing.join(', ')}. Required columns are: ${REQUIRED_CSV_HEADERS.join(', ')}.`);
        return;
      }

      // Valid CSV
      csvFile = file;
      isUsingSample = false;
      hideAlert();

      csvFileName.textContent = file.name;
      csvFileStatus.textContent = `${(file.size / 1024).toFixed(1)} KB • All required columns validated`;
      csvPlaceholder.classList.add('hidden');
      csvInfoContainer.classList.remove('hidden');

      updateAnalyzeButtonState();
    } catch (err) {
      csvFile = null;
      csvInput.value = '';
      csvInfoContainer.classList.add('hidden');
      csvPlaceholder.classList.remove('hidden');
      updateAnalyzeButtonState();
      showAlert('Failed to read CSV file: ' + err.message);
    }
  }

  // File Inputs
  imageInput.addEventListener('change', (e) => {
    handleImageFile(e.target.files[0]);
  });

  csvInput.addEventListener('change', (e) => {
    handleCsvFile(e.target.files[0]);
  });

  // Drag and Drop: Image Dropzone
  ['dragenter', 'dragover'].forEach(eventName => {
    imageDropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      imageDropzone.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    imageDropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      imageDropzone.classList.remove('drag-over');
    });
  });

  imageDropzone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleImageFile(files[0]);
    }
  });

  // Drag and Drop: CSV Dropzone
  ['dragenter', 'dragover'].forEach(eventName => {
    csvDropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      csvDropzone.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    csvDropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      csvDropzone.classList.remove('drag-over');
    });
  });

  csvDropzone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleCsvFile(files[0]);
    }
  });

  // Remove File Handlers
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

    imagePreview.src = '/static/sample_data/sample_product.jpg';
    imagePlaceholder.classList.add('hidden');
    imagePreviewContainer.classList.remove('hidden');

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
            <div class="meta-field meta-field-wide">
              <strong>How to Test</strong>
              ${escapeHtml(h.how_to_test)}
            </div>
          </div>
        `;
        hypothesesList.appendChild(item);
      });
    } else {
      hypothesesList.innerHTML = '<p class="card-explainer">No hypotheses available.</p>';
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
      experimentsList.innerHTML = '<p class="card-explainer">No experiments available.</p>';
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

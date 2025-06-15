// Advanced Monte Carlo Calculator - Frontend Application

class AdvancedMonteCarloApp {
    constructor() {
        this.currentResults = null;
        this.presets = {};
        this.charts = {};
        this.comparisonData = [];
        this.init();
    }

    init() {
        this.loadPresets();
        this.bindEvents();
        this.setupRangeUpdaters();
        this.setupFormValidation();
        this.setupRangeVisualizations();
    }

    async loadPresets() {
        try {
            const response = await fetch('/api/presets');
            const data = await response.json();
            if (data.success) {
                this.presets = data.presets;
            }
        } catch (error) {
            console.error('Error loading presets:', error);
        }
    }

    bindEvents() {
        // Calculate button
        const calculateBtn = document.getElementById('calculateBtn');
        if (calculateBtn) {
            calculateBtn.addEventListener('click', () => {
                this.calculateAdvanced();
            });
        }

        // Preset selection
        document.querySelectorAll('.preset-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const presetKey = e.currentTarget.dataset.preset;
                this.applyPreset(presetKey);
            });
        });

        // Mode change handlers
        document.querySelectorAll('input[name="calculationMode"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.handleModeChange(e.target.value);
            });
        });

        // Deposit type change
        const depositType = document.getElementById('depositType');
        if (depositType) {
            depositType.addEventListener('change', (e) => {
                this.handleDepositTypeChange(e.target.value);
            });
        }

        // Tax system change
        const taxSystem = document.getElementById('taxSystem');
        if (taxSystem) {
            taxSystem.addEventListener('change', (e) => {
                this.handleTaxSystemChange(e.target.value);
            });
        }

        // Parameter change handlers for real-time validation
        this.setupParameterChangeHandlers();
    }

    setupRangeUpdaters() {
        // Range slider value updaters
        const rangeInputs = ['accumulationYears', 'withdrawalYears', 'targetWithdrawalRate'];
        
        rangeInputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', (e) => {
                    this.updateRangeValue(id, e.target.value);
                });
                // Initialize display
                this.updateRangeValue(id, input.value);
            }
        });
    }

    updateRangeValue(id, value) {
        const display = document.getElementById(`${id}-value`);
        if (display) {
            let displayValue = value;
            if (id.includes('Years')) {
                displayValue = `${value} ${value == 1 ? 'год' : value < 5 ? 'года' : 'лет'}`;
            } else if (id.includes('Rate')) {
                displayValue = `${value}%`;
            }
            display.textContent = displayValue;
        }
    }

    setupRangeVisualizations() {
        // Initialize range visualization charts
        this.initializeRangeChart('interestRateChart');
        this.initializeRangeChart('volatilityChart');
        
        // Update charts when parameters change
        ['interestRateMin', 'interestRateMean', 'interestRateMax'].forEach(id => {
            document.getElementById(id).addEventListener('input', () => {
                this.updateRangeChart('interestRateChart', 'interest');
            });
        });
        
        ['volatilityMin', 'volatilityMean', 'volatilityMax'].forEach(id => {
            document.getElementById(id).addEventListener('input', () => {
                this.updateRangeChart('volatilityChart', 'volatility');
            });
        });
    }

    initializeRangeChart(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Simple distribution visualization
        this.drawRangeDistribution(ctx, 5, 15, 10, canvas.width, canvas.height);
    }

    updateRangeChart(canvasId, type) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        let min, mean, max;
        
        if (type === 'interest') {
            min = parseFloat(document.getElementById('interestRateMin').value);
            mean = parseFloat(document.getElementById('interestRateMean').value);
            max = parseFloat(document.getElementById('interestRateMax').value);
        } else {
            min = parseFloat(document.getElementById('volatilityMin').value);
            mean = parseFloat(document.getElementById('volatilityMean').value);
            max = parseFloat(document.getElementById('volatilityMax').value);
        }
        
        this.drawRangeDistribution(ctx, min, max, mean, canvas.width, canvas.height);
    }

    drawRangeDistribution(ctx, min, max, mean, width, height) {
        ctx.clearRect(0, 0, width, height);
        
        // Draw background
        ctx.fillStyle = '#f8f9fa';
        ctx.fillRect(0, 0, width, height);
        
        // Draw distribution curve (simplified beta-like distribution)
        ctx.beginPath();
        ctx.strokeStyle = '#3f51b5';
        ctx.lineWidth = 2;
        
        const points = 100;
        for (let i = 0; i <= points; i++) {
            const x = (i / points) * width;
            const value = min + (max - min) * (i / points);
            
            // Simple bell curve centered on mean
            const normalized = (value - min) / (max - min);
            const meanNorm = (mean - min) / (max - min);
            const distance = Math.abs(normalized - meanNorm);
            const y = height - (height * 0.8 * Math.exp(-distance * distance * 8));
            
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.stroke();
        
        // Draw mean line
        const meanX = ((mean - min) / (max - min)) * width;
        ctx.beginPath();
        ctx.strokeStyle = '#f44336';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.moveTo(meanX, 10);
        ctx.lineTo(meanX, height - 10);
        ctx.stroke();
        ctx.setLineDash([]);
        
        // Draw labels
        ctx.fillStyle = '#666';
        ctx.font = '10px Inter';
        ctx.textAlign = 'left';
        ctx.fillText(`${min.toFixed(1)}%`, 5, height - 5);
        ctx.textAlign = 'center';
        ctx.fillText(`${mean.toFixed(1)}%`, meanX, height - 5);
        ctx.textAlign = 'right';
        ctx.fillText(`${max.toFixed(1)}%`, width - 5, height - 5);
    }

    setupParameterChangeHandlers() {
        // Real-time parameter validation and updates
        const parameterInputs = [
            'initialAmount', 'monthlyDeposit', 'interestRateMin', 'interestRateMax', 
            'interestRateMean', 'volatilityMin', 'volatilityMax', 'volatilityMean',
            'inflationRate', 'taxRate', 'managementFee'
        ];
        
        parameterInputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => {
                    this.validateParameter(id, input.value);
                });
                input.addEventListener('blur', () => {
                    this.validateParameter(id, input.value);
                });
            }
        });
    }

    validateParameter(id, value) {
        const input = document.getElementById(id);
        if (!input) return true; // Если элемент не найден, считаем валидным
        
        const numValue = parseFloat(value);
        
        // Clear previous validation
        input.classList.remove('is-invalid', 'is-valid');
        
        // Validate based on parameter type
        let isValid = true;
        let message = '';
        
        if (isNaN(numValue)) {
            isValid = false;
            message = 'Значение должно быть числом';
        } else if (id.includes('Amount') && numValue < 0) {
            isValid = false;
            message = 'Сумма должна быть положительной';
        } else if (id.includes('Years') && (numValue < 1 || numValue > 100)) {
            isValid = false;
            message = 'Период должен быть от 1 до 100 лет';
        } else if (id.includes('interestRate') && (numValue < -50 || numValue > 100)) {
            isValid = false;
            message = 'Доходность должна быть от -50% до 100%';
        } else if (id.includes('volatility') && (numValue < 0 || numValue > 100)) {
            isValid = false;
            message = 'Волатильность должна быть от 0% до 100%';
        } else if (id === 'inflationRate' && (numValue < 0 || numValue > 20)) {
            isValid = false;
            message = 'Инфляция должна быть от 0% до 20%';
        }
        
        // Check range validity for min/max parameters
        if (id.includes('Min') || id.includes('Max') || id.includes('Mean')) {
            const baseId = id.replace(/Min|Max|Mean/, '');
            const min = parseFloat(document.getElementById(baseId + 'Min').value);
            const max = parseFloat(document.getElementById(baseId + 'Max').value);
            const mean = parseFloat(document.getElementById(baseId + 'Mean').value);
            
            if (min >= max) {
                isValid = false;
                message = 'Минимум должен быть меньше максимума';
            } else if (mean < min || mean > max) {
                isValid = false;
                message = 'Среднее значение должно быть между минимумом и максимумом';
            }
        }
        
        if (isValid) {
            input.classList.add('is-valid');
        } else {
            input.classList.add('is-invalid');
            this.showFieldError(input, message);
        }
        
        return isValid;
    }

    showFieldError(input, message) {
        // Remove existing feedback
        const existingFeedback = input.parentNode.querySelector('.invalid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        // Add new feedback
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = message;
        input.parentNode.appendChild(feedback);
    }

    handleModeChange(mode) {
        // Show/hide withdrawal period section based on mode
        const withdrawalContainer = document.getElementById('withdrawalYearsContainer');
        
        if (withdrawalContainer) {
            if (mode === 'accumulation') {
                withdrawalContainer.style.display = 'none';
            } else {
                withdrawalContainer.style.display = 'block';
            }
        }
        
        // Update UI indicators
        this.updateModeIndicators(mode);
    }

    updateModeIndicators(mode) {
        const indicators = {
            'accumulation': { icon: 'chart-line', color: 'primary', text: 'Накопление' },
            'withdrawal': { icon: 'hand-holding-usd', color: 'warning', text: 'Снятие' },
            'mixed': { icon: 'sync-alt', color: 'success', text: 'Полный цикл' }
        };
        
        const indicator = indicators[mode];
        const modeDisplay = document.getElementById('currentModeDisplay');
        if (modeDisplay) {
            modeDisplay.innerHTML = `
                <i class=\"fas fa-${indicator.icon} me-2 text-${indicator.color}\"></i>
                ${indicator.text}
            `;
        }
    }

    handleDepositTypeChange(type) {
        const monthlyContainer = document.getElementById('monthlyDepositContainer');
        const lumpSumContainer = document.getElementById('lumpSumContainer');
        
        if (type === 'monthly') {
            monthlyContainer.style.display = 'block';
            if (lumpSumContainer) lumpSumContainer.style.display = 'none';
        } else if (type === 'lump_sum') {
            monthlyContainer.style.display = 'none';
            if (lumpSumContainer) lumpSumContainer.style.display = 'block';
        } else {
            monthlyContainer.style.display = 'block';
            if (lumpSumContainer) lumpSumContainer.style.display = 'block';
        }
    }

    handleTaxSystemChange(system) {
        const taxRateContainer = document.getElementById('taxRateContainer');
        const taxRateInput = document.getElementById('taxRate');
        
        if (system === 'none') {
            taxRateContainer.style.display = 'none';
        } else {
            taxRateContainer.style.display = 'block';
            
            if (system === 'german') {
                taxRateInput.value = 26.375;
            } else if (system === 'simple') {
                taxRateInput.value = 25.0;
            }
        }
    }

    applyPreset(presetKey) {
        const preset = this.presets[presetKey];
        if (!preset) return;
        
        // Update all form fields
        document.getElementById('initialAmount').value = preset.initial_amount;
        document.getElementById('monthlyDeposit').value = preset.monthly_deposit;
        document.getElementById('interestRateMin').value = preset.interest_rate_min;
        document.getElementById('interestRateMax').value = preset.interest_rate_max;
        document.getElementById('interestRateMean').value = preset.interest_rate_mean;
        document.getElementById('volatilityMin').value = preset.volatility_min;
        document.getElementById('volatilityMax').value = preset.volatility_max;
        document.getElementById('volatilityMean').value = preset.volatility_mean;
        document.getElementById('accumulationYears').value = preset.accumulation_years;
        document.getElementById('withdrawalYears').value = preset.withdrawal_years;
        document.getElementById('targetWithdrawalRate').value = preset.target_withdrawal_rate;
        document.getElementById('inflationRate').value = preset.inflation_rate;
        
        // Update range displays
        this.updateRangeValue('accumulationYears', preset.accumulation_years);
        this.updateRangeValue('withdrawalYears', preset.withdrawal_years);
        this.updateRangeValue('targetWithdrawalRate', preset.target_withdrawal_rate);
        
        // Update range charts
        this.updateRangeChart('interestRateChart', 'interest');
        this.updateRangeChart('volatilityChart', 'volatility');
        
        // Update preset selection
        document.querySelectorAll('.preset-card').forEach(card => {
            card.classList.remove('active');
        });
        document.querySelector(`[data-preset=\"${presetKey}\"]`).classList.add('active');
        
        // Set calculation mode to mixed for comprehensive analysis
        document.getElementById('mode-mixed').checked = true;
        this.handleModeChange('mixed');
        
        this.showNotification(`Применена стратегия: ${preset.name}`, 'info');
    }

    async calculateAdvanced() {
        console.log('Calculate button clicked');
        
        const btn = document.getElementById('calculateBtn');
        const spinner = document.getElementById('loadingSpinner');
        const btnText = btn.querySelector('span') || btn;
        
        // Validate all parameters
        if (!this.validateAllParameters()) {
            console.log('Validation failed');
            this.showNotification('Пожалуйста, исправьте ошибки в параметрах', 'error');
            return;
        }
        
        console.log('Validation passed');
        
        // Show loading state
        btn.disabled = true;
        spinner.classList.remove('d-none');
        if (btnText !== btn) btnText.textContent = 'Анализируем...';
        
        try {
            const parameters = this.getAdvancedParameters();
            console.log('Parameters:', parameters);
            
            const response = await fetch('/api/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    calculation_type: 'advanced',
                    ...parameters
                })
            });
            
            console.log('Response status:', response.status);
            const result = await response.json();
            console.log('Result:', result);
            
            if (result.success) {
                this.currentResults = result.data;
                this.displayAdvancedResults(result.data);
                this.showNotification('Анализ завершен успешно!', 'success');
            } else {
                throw new Error(result.error || 'Ошибка расчета');
            }
            
        } catch (error) {
            console.error('Calculation error:', error);
            this.showNotification(`Ошибка: ${error.message}`, 'error');
        } finally {
            // Hide loading state
            btn.disabled = false;
            spinner.classList.add('d-none');
            if (btnText !== btn) btnText.textContent = 'Рассчитать';
        }
    }

    validateAllParameters() {
        // Только видимые input поля, не hidden
        const parameterInputs = document.querySelectorAll('input[type=\"number\"]:not([type=\"hidden\"]), select:not([type=\"hidden\"])');
        let isValid = true;
        
        console.log('Validating parameters:', parameterInputs.length);
        
        parameterInputs.forEach(input => {
            // Пропускаем скрытые элементы
            if (input.style.display === 'none' || input.type === 'hidden') {
                return;
            }
            
            if (input.type === 'number') {
                const result = this.validateParameter(input.id, input.value);
                console.log(`Validating ${input.id}: ${input.value} = ${result}`);
                if (!result) {
                    isValid = false;
                }
            }
        });
        
        console.log('Overall validation result:', isValid);
        return isValid;
    }

    getAdvancedParameters() {
        const mode = document.querySelector('input[name=\"calculationMode\"]:checked').value;
        
        return {
            calculation_mode: mode,
            deposit_type: document.getElementById('depositType').value,
            initial_amount: parseFloat(document.getElementById('initialAmount').value),
            monthly_deposit: parseFloat(document.getElementById('monthlyDeposit').value),
            
            interest_rate_min: parseFloat(document.getElementById('interestRateMin').value),
            interest_rate_max: parseFloat(document.getElementById('interestRateMax').value),
            interest_rate_mean: parseFloat(document.getElementById('interestRateMean').value),
            
            volatility_min: parseFloat(document.getElementById('volatilityMin').value),
            volatility_max: parseFloat(document.getElementById('volatilityMax').value),
            volatility_mean: parseFloat(document.getElementById('volatilityMean').value),
            
            accumulation_years: parseInt(document.getElementById('accumulationYears').value),
            withdrawal_years: parseInt(document.getElementById('withdrawalYears').value),
            
            inflation_rate: parseFloat(document.getElementById('inflationRate').value),
            inflation_volatility: parseFloat(document.getElementById('inflationVolatility').value),
            
            tax_system: document.getElementById('taxSystem').value,
            tax_rate: parseFloat(document.getElementById('taxRate').value),
            
            target_withdrawal_rate: parseFloat(document.getElementById('targetWithdrawalRate').value),
            withdrawal_strategy: document.getElementById('withdrawalStrategy').value,
            
            management_fee: parseFloat(document.getElementById('managementFee').value),
            consider_sequence_risk: document.getElementById('considerSequenceRisk').checked,
            
            iterations: parseInt(document.getElementById('iterations').value)
        };
    }

    displayAdvancedResults(data) {
        console.log('Displaying results:', data);
        
        // Show results section
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.classList.remove('d-none');
        }
        
        // Update summary dashboard
        this.updateSummaryDashboard(data);
        
        // Display calculation details
        this.displayCalculationDetails(data);
        
        // Create a simple chart
        this.createSimpleChart(data);
        
        // Scroll to results
        setTimeout(() => {
            document.getElementById('resultsSection').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }, 300);
    }

    updateSummaryDashboard(data) {
        console.log('Updating summary dashboard with data:', data);
        
        let totalInvested = 0;
        let expectedValue = 0;
        let monthlyIncome = 0;
        let successProbability = 0;
        
        if (data.accumulation_phase) {
            totalInvested = data.accumulation_phase.total_invested || 0;
            expectedValue = data.accumulation_phase.nominal_stats?.mean || data.accumulation_phase.expected_value || 0;
        }
        
        if (data.withdrawal_phase) {
            successProbability = data.withdrawal_phase.success_probability || 0;
            if (data.withdrawal_phase.monthly_income_stats) {
                monthlyIncome = data.withdrawal_phase.monthly_income_stats.mean_monthly_income || 0;
            }
        }
        
        // Update elements if they exist
        const totalInvestedEl = document.getElementById('totalInvested');
        const expectedValueEl = document.getElementById('expectedValue');
        const monthlyIncomeEl = document.getElementById('monthlyIncome');
        const successProbabilityEl = document.getElementById('successProbability');
        
        if (totalInvestedEl) totalInvestedEl.textContent = this.formatCurrency(totalInvested);
        if (expectedValueEl) expectedValueEl.textContent = this.formatCurrency(expectedValue);
        if (monthlyIncomeEl) monthlyIncomeEl.textContent = this.formatCurrency(monthlyIncome);
        if (successProbabilityEl) successProbabilityEl.textContent = `${Math.round(successProbability * 100)}%`;
    }
    
    displayCalculationDetails(data) {
        const detailsEl = document.getElementById('calculationDetails');
        if (!detailsEl) return;
        
        let details = '<h6>📊 Результаты Monte Carlo симуляции:</h6><ul>';
        
        if (data.accumulation_phase) {
            const phase = data.accumulation_phase;
            details += `<li><strong>Общие инвестиции:</strong> ${this.formatCurrency(phase.total_invested || 0)}</li>`;
            details += `<li><strong>Ожидаемая стоимость:</strong> ${this.formatCurrency(phase.nominal_stats?.mean || phase.expected_value || 0)}</li>`;
            
            if (phase.inflation_impact) {
                details += `<li><strong>Реальная покупательная способность:</strong> ${this.formatCurrency(phase.inflation_impact.real_value || 0)}</li>`;
                details += `<li><strong>Потеря от инфляции:</strong> ${(phase.inflation_impact.purchasing_power_loss || 0).toFixed(1)}%</li>`;
            }
        }
        
        if (data.withdrawal_phase) {
            const phase = data.withdrawal_phase;
            details += `<li><strong>Вероятность успеха:</strong> ${Math.round((phase.success_probability || 0) * 100)}%</li>`;
            if (phase.monthly_income_stats) {
                details += `<li><strong>Средний ежемесячный доход:</strong> ${this.formatCurrency(phase.monthly_income_stats.mean_monthly_income || 0)}</li>`;
            }
        }
        
        details += '</ul>';
        detailsEl.innerHTML = details;
    }
    
    createSimpleChart(data) {
        const ctx = document.getElementById('mainChart');
        if (!ctx || !data.accumulation_phase) return;
        
        // Clear any existing chart
        if (this.currentChart) {
            this.currentChart.destroy();
        }
        
        const progression = data.accumulation_phase.monthly_progression;
        if (!progression) return;
        
        this.currentChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: progression.months.map(m => `${Math.floor(m/12)}г ${m%12}м`),
                datasets: [{
                    label: 'Средний баланс портфеля',
                    data: progression.mean_balance,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 2,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Время'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Стоимость портфеля (€)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '€' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Рост портфеля во времени'
                    },
                    legend: {
                        display: true
                    }
                }
            }
        });
    }

    displayAccumulationResults(data) {
        const container = document.getElementById('accumulationStats');
        
        let html = `
            <div class=\"stats-panel\">
                <h6 class=\"text-primary mb-3\">Номинальные значения</h6>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Среднее значение:</span>
                    <span class=\"stat-value\">${this.formatCurrency(data.nominal_stats.mean)}</span>
                </div>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Медиана:</span>
                    <span class=\"stat-value\">${this.formatCurrency(data.nominal_stats.median)}</span>
                </div>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Стандартное отклонение:</span>
                    <span class=\"stat-value\">${this.formatCurrency(data.nominal_stats.std)}</span>
                </div>
            </div>
            
            <div class=\"stats-panel\">
                <h6 class=\"text-success mb-3\">Реальные значения (с учетом инфляции)</h6>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Реальная стоимость:</span>
                    <span class=\"stat-value\">${this.formatCurrency(data.real_stats.mean)}</span>
                </div>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Потеря покупательной способности:</span>
                    <span class=\"stat-value text-warning\">${data.inflation_impact.purchasing_power_loss.toFixed(1)}%</span>
                </div>
            </div>
            
            <div class=\"stats-panel\">
                <h6 class=\"text-info mb-3\">После налогов</h6>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Стоимость после налогов:</span>
                    <span class=\"stat-value\">${this.formatCurrency(data.after_tax_stats.mean)}</span>
                </div>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Налоговые потери:</span>
                    <span class=\"stat-value text-danger\">${data.tax_impact.tax_cost_percent.toFixed(1)}%</span>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        
        // Create accumulation chart
        this.createAccumulationChart(data);
    }

    displayWithdrawalResults(data) {
        const container = document.getElementById('withdrawalStats');
        const swrContainer = document.getElementById('swrAnalysis');
        
        let html = `
            <div class=\"stats-panel\">
                <h6 class=\"text-primary mb-3\">Фаза снятия</h6>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Начальная сумма:</span>
                    <span class=\"stat-value\">${this.formatCurrency(data.start_amount)}</span>
                </div>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Вероятность успеха:</span>
                    <span class=\"stat-value\">${data.success_probability.toFixed(1)}%</span>
                </div>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Рекомендуемая SWR:</span>
                    <span class=\"stat-value\">${data.recommended_swr.toFixed(2)}%</span>
                </div>
            </div>
        `;
        
        if (data.monthly_income_stats) {
            html += `
                <div class=\"stats-panel\">
                    <h6 class=\"text-success mb-3\">Ежемесячный доход</h6>
                    <div class=\"stat-item\">
                        <span class=\"stat-label\">Средний доход:</span>
                        <span class=\"stat-value\">${this.formatCurrency(data.monthly_income_stats.mean_monthly_income)}</span>
                    </div>
                    <div class=\"stat-item\">
                        <span class=\"stat-label\">Медиана дохода:</span>
                        <span class=\"stat-value\">${this.formatCurrency(data.monthly_income_stats.median_monthly_income)}</span>
                    </div>
                </div>
            `;
        }
        
        container.innerHTML = html;
        
        // SWR Analysis
        if (data.swr_analysis) {
            let swrHtml = `
                <div class=\"stats-panel\">
                    <h6 class=\"text-warning mb-3\">Анализ безопасного уровня снятия</h6>
                    <div class=\"stat-item\">
                        <span class=\"stat-label\">SWR (95% успеха):</span>
                        <span class=\"stat-value\">${data.swr_analysis.swr_95_percent.toFixed(2)}%</span>
                    </div>
                    <div class=\"stat-item\">
                        <span class=\"stat-label\">SWR (90% успеха):</span>
                        <span class=\"stat-value\">${data.swr_analysis.swr_90_percent.toFixed(2)}%</span>
                    </div>
                    <div class=\"stat-item\">
                        <span class=\"stat-label\">SWR (80% успеха):</span>
                        <span class=\"stat-value\">${data.swr_analysis.swr_80_percent.toFixed(2)}%</span>
                    </div>
                </div>
            `;
            swrContainer.innerHTML = swrHtml;
        }
        
        // Create withdrawal chart
        this.createWithdrawalChart(data);
    }

    displayRiskAnalysis(riskMetrics) {
        const container = document.getElementById('riskMetrics');
        
        let html = '<div class=\"stats-panel\"><h6 class=\"text-danger mb-3\">Метрики риска</h6>';
        
        if (riskMetrics.accumulation) {
            const acc = riskMetrics.accumulation;
            html += `
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Волатильность портфеля:</span>
                    <span class=\"stat-value\">${acc.volatility.toFixed(2)}%</span>
                </div>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Риск снижения:</span>
                    <span class=\"stat-value\">${this.formatCurrency(acc.downside_risk)}</span>
                </div>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Макс. просадка:</span>
                    <span class=\"stat-value\">${acc.max_drawdown.toFixed(2)}%</span>
                </div>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">VaR (95%):</span>
                    <span class=\"stat-value\">${this.formatCurrency(acc.var_95)}</span>
                </div>
            `;
        }
        
        if (riskMetrics.withdrawal) {
            const with_ = riskMetrics.withdrawal;
            html += `
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Вероятность неудачи:</span>
                    <span class=\"stat-value\">${with_.failure_probability.toFixed(1)}%</span>
                </div>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Риск последовательности:</span>
                    <span class=\"stat-value\">${with_.sequence_risk.toFixed(1)}</span>
                </div>
            `;
        }
        
        html += '</div>';
        container.innerHTML = html;
        
        // Create risk chart
        this.createRiskChart(riskMetrics);
    }

    displayEconomicImpact(accumulationData) {
        const inflationContainer = document.getElementById('inflationImpact');
        const taxContainer = document.getElementById('taxImpact');
        
        // Inflation impact
        const inflationHtml = `
            <div class=\"stats-panel\">
                <h6 class=\"text-info mb-3\">Влияние инфляции</h6>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Номинальная стоимость:</span>
                    <span class=\"stat-value\">${this.formatCurrency(accumulationData.inflation_impact.nominal_value)}</span>
                </div>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Реальная стоимость:</span>
                    <span class=\"stat-value\">${this.formatCurrency(accumulationData.inflation_impact.real_value)}</span>
                </div>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Потеря покупательной способности:</span>
                    <span class=\"stat-value text-warning\">${accumulationData.inflation_impact.purchasing_power_loss.toFixed(1)}%</span>
                </div>
            </div>
        `;
        
        // Tax impact
        const taxHtml = `
            <div class=\"stats-panel\">
                <h6 class=\"text-danger mb-3\">Налоговое воздействие</h6>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">До налогов:</span>
                    <span class=\"stat-value\">${this.formatCurrency(accumulationData.tax_impact.pre_tax_value)}</span>
                </div>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">После налогов:</span>
                    <span class=\"stat-value\">${this.formatCurrency(accumulationData.tax_impact.after_tax_value)}</span>
                </div>
                <div class=\"stat-item\">
                    <span class=\"stat-label\">Налоговые потери:</span>
                    <span class=\"stat-value text-danger\">${accumulationData.tax_impact.tax_cost_percent.toFixed(1)}%</span>
                </div>
            </div>
        `;
        
        inflationContainer.innerHTML = inflationHtml;
        taxContainer.innerHTML = taxHtml;
    }

    createAccumulationChart(data) {
        const ctx = document.getElementById('accumulationChart');
        if (!ctx) return;
        
        // Destroy existing chart
        if (this.charts.accumulation) {
            this.charts.accumulation.destroy();
        }
        
        const progression = data.monthly_progression;
        
        this.charts.accumulation = new Chart(ctx, {
            type: 'line',
            data: {
                labels: progression.months.map(m => `${Math.floor(m/12)}г ${m%12}м`),
                datasets: [{
                    label: 'Среднее значение',
                    data: progression.mean_balance,
                    borderColor: '#3f51b5',
                    backgroundColor: 'rgba(63, 81, 181, 0.1)',
                    fill: false,
                    tension: 0.1
                }, {
                    label: '95-й процентиль',
                    data: progression.percentile_95,
                    borderColor: '#4caf50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    fill: false,
                    borderDash: [5, 5]
                }, {
                    label: '5-й процентиль',
                    data: progression.percentile_5,
                    borderColor: '#f44336',
                    backgroundColor: 'rgba(244, 67, 54, 0.1)',
                    fill: false,
                    borderDash: [5, 5]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Рост портфеля во времени'
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return app.formatCurrency(value);
                            }
                        }
                    }
                }
            }
        });
    }

    createWithdrawalChart(data) {
        const ctx = document.getElementById('withdrawalChart');
        if (!ctx || !data.swr_analysis) return;
        
        // Destroy existing chart
        if (this.charts.withdrawal) {
            this.charts.withdrawal.destroy();
        }
        
        const swrData = data.swr_analysis.success_rates_by_swr;
        const labels = Object.keys(swrData).map(rate => `${rate}%`);
        const values = Object.values(swrData);
        
        this.charts.withdrawal = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Вероятность успеха (%)',
                    data: values,
                    borderColor: '#ff9800',
                    backgroundColor: 'rgba(255, 152, 0, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Вероятность успеха по уровням SWR'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    createRiskChart(riskMetrics) {
        const ctx = document.getElementById('riskChart');
        if (!ctx) return;
        
        // Destroy existing chart
        if (this.charts.risk) {
            this.charts.risk.destroy();
        }
        
        // Create risk radar chart
        const labels = ['Волатильность', 'Риск снижения', 'Макс. просадка', 'Риск неудачи', 'Риск последовательности'];
        const values = [];
        
        if (riskMetrics.accumulation) {
            values.push(
                Math.min(riskMetrics.accumulation.volatility, 100),
                Math.min((riskMetrics.accumulation.downside_risk / 10000) * 100, 100),
                Math.min(riskMetrics.accumulation.max_drawdown, 100)
            );
        } else {
            values.push(0, 0, 0);
        }
        
        if (riskMetrics.withdrawal) {
            values.push(
                Math.min(riskMetrics.withdrawal.failure_probability, 100),
                Math.min(riskMetrics.withdrawal.sequence_risk, 100)
            );
        } else {
            values.push(0, 0);
        }
        
        this.charts.risk = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Уровень риска (%)',
                    data: values,
                    borderColor: '#f44336',
                    backgroundColor: 'rgba(244, 67, 54, 0.2)',
                    pointBackgroundColor: '#f44336'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Профиль рисков портфеля'
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    setupFormValidation() {
        // Enhanced form validation for advanced parameters
        const form = document.querySelector('#parameterTabs').closest('.card');
        if (!form) return;
        
        // Add validation indicators
        const requiredInputs = form.querySelectorAll('input[required], select[required]');
        requiredInputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateParameter(input.id, input.value);
            });
        });
    }

    showNotification(message, type = 'info') {
        // Enhanced notification system
        const notification = document.createElement('div');
        notification.className = `alert alert-${this.getBootstrapAlertClass(type)} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 1060; min-width: 350px; max-width: 500px;';
        
        const icon = this.getNotificationIcon(type);
        notification.innerHTML = `
            <div class=\"d-flex align-items-center\">
                ${icon}
                <div class=\"flex-grow-1\">${message}</div>
                <button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    getBootstrapAlertClass(type) {
        const mapping = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        return mapping[type] || 'info';
    }

    getNotificationIcon(type) {
        const icons = {
            'success': '<i class=\"fas fa-check-circle me-2 text-success\"></i>',
            'error': '<i class=\"fas fa-exclamation-circle me-2 text-danger\"></i>',
            'warning': '<i class=\"fas fa-exclamation-triangle me-2 text-warning\"></i>',
            'info': '<i class=\"fas fa-info-circle me-2 text-info\"></i>'
        };
        return icons[type] || icons.info;
    }

    formatCurrency(value) {
        if (typeof value !== 'number' || isNaN(value)) return '—';
        
        return new Intl.NumberFormat('de-DE', {
            style: 'currency',
            currency: 'EUR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }

    formatPercentage(value) {
        if (typeof value !== 'number' || isNaN(value)) return '—';
        
        return new Intl.NumberFormat('de-DE', {
            style: 'percent',
            minimumFractionDigits: 1,
            maximumFractionDigits: 1
        }).format(value / 100);
    }
}

// Global functions
function updateRangeValue(id, value) {
    if (window.app) {
        window.app.updateRangeValue(id, value);
    }
}

function showComparison() {
    // Show comparison modal
    const modal = new bootstrap.Modal(document.getElementById('comparisonModal'));
    modal.show();
    
    // Load comparison content
    if (window.app) {
        window.app.loadComparisonContent();
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AdvancedMonteCarloApp();
});
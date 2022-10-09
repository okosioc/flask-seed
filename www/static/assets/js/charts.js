//
// charts.js
// Theme module
//

'use strict';

(function () {

    //
    // Variables
    //

    var colors = {
        gray: {
            300: '#E3EBF6',
            600: '#95AAC9',
            700: '#6E84A3',
            800: '#152E4D',
            900: '#283E59'
        },
        primary: {
            100: '#D2DDEC',
            300: '#A6C5F7',
            700: '#2C7BE5',
        },
        black: '#12263F',
        white: '#FFFFFF',
        transparent: 'transparent',
    };

    var fonts = {
        base: 'Cerebri Sans'
    };

    var toggles = document.querySelectorAll('[data-toggle="chart"]');
    var legends = document.querySelectorAll('[data-toggle="legend"]');

    //
    // Functions
    //

    function globalOptions() {

        // Global
        Chart.defaults.global.responsive = true;
        Chart.defaults.global.maintainAspectRatio = false;

        // Default
        Chart.defaults.global.defaultColor = colors.gray[600];
        Chart.defaults.global.defaultFontColor = colors.gray[600];
        Chart.defaults.global.defaultFontFamily = fonts.base;
        Chart.defaults.global.defaultFontSize = 13;

        // Layout
        Chart.defaults.global.layout.padding = 0;

        // Legend
        Chart.defaults.global.legend.display = false;
        Chart.defaults.global.legend.position = 'bottom';
        Chart.defaults.global.legend.labels.usePointStyle = true;
        Chart.defaults.global.legend.labels.padding = 16;

        // Point
        Chart.defaults.global.elements.point.radius = 0;
        Chart.defaults.global.elements.point.backgroundColor = colors.primary[700];

        // Line
        Chart.defaults.global.elements.line.tension = .4;
        Chart.defaults.global.elements.line.borderWidth = 3;
        Chart.defaults.global.elements.line.borderColor = colors.primary[700];
        Chart.defaults.global.elements.line.backgroundColor = colors.transparent;
        Chart.defaults.global.elements.line.borderCapStyle = 'rounded';

        // Rectangle
        Chart.defaults.global.elements.rectangle.backgroundColor = colors.primary[700];
        Chart.defaults.global.elements.rectangle.maxBarThickness = 10;

        // Arc
        Chart.defaults.global.elements.arc.backgroundColor = colors.primary[700];
        Chart.defaults.global.elements.arc.borderColor = colors.white;
        Chart.defaults.global.elements.arc.borderWidth = 4;
        Chart.defaults.global.elements.arc.hoverBorderColor = colors.white;

        // Tooltips
        Chart.defaults.global.tooltips.enabled = false;
        Chart.defaults.global.tooltips.mode = 'index';
        Chart.defaults.global.tooltips.intersect = false;
        Chart.defaults.global.tooltips.custom = function (model) {
            var tooltip = document.getElementById('chart-tooltip');
            var chartType = this._chart.config.type;

            // Create tooltip if doesn't exist
            if (!tooltip) {
                tooltip = document.createElement('div');

                tooltip.setAttribute('id', 'chart-tooltip');
                tooltip.setAttribute('role', 'tooltip');
                tooltip.classList.add('popover');
                tooltip.classList.add('bs-popover-top');

                document.body.appendChild(tooltip);
            }

            // Hide tooltip if not visible
            if (model.opacity === 0) {
                tooltip.style.visibility = 'hidden';

                return;
            }

            if (model.body) {
                var title = model.title || [];
                var body = model.body.map(function (body) {
                    return body.lines;
                });

                // Add arrow
                var content = '<div class="arrow"></div>';

                // Add title
                title.forEach(function (title) {
                    content += '<h3 class="popover-header text-center">' + title + '</h3>';
                });

                // Add content
                body.forEach(function (body, i) {
                    var colors = model.labelColors[i];
                    var indicatorColor = (chartType === 'line' && colors.borderColor !== 'rgba(0,0,0,0.1)') ? colors.borderColor : colors.backgroundColor;
                    var indicator = '<span class="popover-body-indicator" style="background-color: ' + indicatorColor + '"></span>';
                    var justifyContent = (body.length > 1) ? 'justify-content-left' : 'justify-content-center';

                    content += '<div class="popover-body d-flex align-items-center ' + justifyContent + '">' + indicator + body + '</div>';
                });

                tooltip.innerHTML = content;
            }

            var canvas = this._chart.canvas;
            var canvasRect = canvas.getBoundingClientRect();

            var scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
            var scrollLeft = window.pageXOffset || document.documentElement.scrollLeft || document.body.scrollLeft || 0;

            var canvasTop = canvasRect.top + scrollTop;
            var canvasLeft = canvasRect.left + scrollLeft;

            var tooltipWidth = tooltip.offsetWidth;
            var tooltipHeight = tooltip.offsetHeight;

            var top = canvasTop + model.caretY - tooltipHeight - 16;
            var left = canvasLeft + model.caretX - tooltipWidth / 2;

            tooltip.style.top = top + 'px';
            tooltip.style.left = left + 'px';
            tooltip.style.visibility = 'visible';
        };

        Chart.defaults.global.tooltips.callbacks.label = function (item, data) {
            var content = '';

            var value = item.yLabel;
            var dataset = data.datasets[item.datasetIndex]
            var label = dataset.label;

            var yAxisID = dataset.yAxisID ? dataset.yAxisID : 0;
            var yAxes = this._chart.options.scales.yAxes;
            var yAxis = yAxes[0];

            if (yAxisID) {
                var yAxis = yAxes.filter(function (item) {
                    return item.id == yAxisID;
                })[0];
            }

            var callback = yAxis.ticks.callback;

            var activeDatasets = data.datasets.filter(function (dataset) {
                return !dataset.hidden;
            });

            if (activeDatasets.length > 1) {
                content = '<span class="popover-body-label mr-auto">' + label + '</span>';
            }

            content += '<span class="popover-body-value">' + callback(value) + '</span>';

            return content;
        };

        // Doughnut
        Chart.defaults.doughnut.cutoutPercentage = 83;
        Chart.defaults.doughnut.tooltips.callbacks.title = function (item, data) {
            return data.labels[item[0].index];
        };
        Chart.defaults.doughnut.tooltips.callbacks.label = function (item, data) {
            var value = data.datasets[0].data[item.index];
            var callbacks = this._chart.options.tooltips.callbacks;
            var afterLabel = callbacks.afterLabel() ? callbacks.afterLabel() : '';
            var beforeLabel = callbacks.beforeLabel() ? callbacks.beforeLabel() : '';
            return '<span class="popover-body-value">' + beforeLabel + value + afterLabel + '</span>';
        };
        Chart.defaults.doughnut.legendCallback = function (chart) {
            var data = chart.data;
            var content = '';
            data.labels.forEach(function (label, index) {
                var bgColor = data.datasets[0].backgroundColor[index];
                content += '<span class="chart-legend-item">';
                content += '<i class="chart-legend-indicator" style="background-color: ' + bgColor + '"></i>';
                content += label;
                content += '</span>';
            });
            return content;
        };
        // Inner text of doughnut chart
        Chart.pluginService.register({
            beforeDraw: function (chart) {
                if (chart.config.options.elements.center) {
                    // Get ctx from string
                    var ctx = chart.chart.ctx;

                    // Get options from the center object in options
                    var centerConfig = chart.config.options.elements.center;
                    var fontStyle = centerConfig.fontStyle || 'Arial';
                    var txt = centerConfig.text;
                    var color = centerConfig.color || '#000';
                    var maxFontSize = centerConfig.maxFontSize || 75;
                    var sidePadding = centerConfig.sidePadding || 20;
                    var sidePaddingCalculated = (sidePadding / 100) * (chart.innerRadius * 2)
                    // Start with a base font of 24px
                    ctx.font = "24px " + fontStyle;

                    // Get the width of the string and also the width of the element minus 10 to give it 5px side padding
                    var stringWidth = ctx.measureText(txt).width;
                    var elementWidth = (chart.innerRadius * 2) - sidePaddingCalculated;

                    // Find out how much the font can grow in width.
                    var widthRatio = elementWidth / stringWidth;
                    var newFontSize = Math.floor(24 * widthRatio);
                    var elementHeight = (chart.innerRadius * 2);

                    // Pick a new font size so it will not be larger than the height of label.
                    var fontSizeToUse = Math.min(newFontSize, elementHeight, maxFontSize);
                    var minFontSize = centerConfig.minFontSize;
                    var lineHeight = centerConfig.lineHeight || 24;
                    var wrapText = false;

                    if (minFontSize === undefined) {
                        minFontSize = 20;
                    }

                    if (minFontSize && fontSizeToUse < minFontSize) {
                        fontSizeToUse = minFontSize;
                        wrapText = true;
                    }

                    // Set font settings to draw it correctly.
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    var centerX = ((chart.chartArea.left + chart.chartArea.right) / 2);
                    var centerY = ((chart.chartArea.top + chart.chartArea.bottom) / 2);
                    ctx.font = fontSizeToUse + "px " + fontStyle;
                    ctx.fillStyle = color;

                    if (!wrapText) {
                        ctx.fillText(txt, centerX, centerY);
                        return;
                    }

                    var words = txt.split(' ');
                    var line = '';
                    var lines = [];

                    // Break words up into multiple lines if necessary
                    for (var n = 0; n < words.length; n++) {
                        var testLine = line + words[n] + ' ';
                        var metrics = ctx.measureText(testLine);
                        var testWidth = metrics.width;
                        if (testWidth > elementWidth && n > 0) {
                            lines.push(line);
                            line = words[n] + ' ';
                        } else {
                            line = testLine;
                        }
                    }

                    // Move the center up depending on line height and number of lines
                    centerY -= (lines.length / 2) * lineHeight;

                    for (var n = 0; n < lines.length; n++) {
                        ctx.fillText(lines[n], centerX, centerY);
                        centerY += lineHeight;
                    }
                    //Draw text in center
                    ctx.fillText(line, centerX, centerY);
                }
            }
        });

        // yAxes
        Chart.scaleService.updateScaleDefaults('linear', {
            gridLines: {
                borderDash: [2],
                borderDashOffset: [2],
                color: colors.gray[300],
                drawBorder: false,
                drawTicks: false,
                zeroLineColor: colors.gray[300],
                zeroLineBorderDash: [2],
                zeroLineBorderDashOffset: [2]
            },
            ticks: {
                beginAtZero: true,
                padding: 10,
                stepSize: 10
            }
        });

        // xAxes
        Chart.scaleService.updateScaleDefaults('category', {
            gridLines: {
                drawBorder: false,
                drawOnChartArea: false,
                drawTicks: false
            },
            ticks: {
                padding: 20
            }
        });
    }

    function getChartInstance(chart) {
        var chartInstance = undefined;

        Chart.helpers.each(Chart.instances, function (instance) {
            if (chart == instance.chart.canvas) {
                chartInstance = instance;
            }
        });

        return chartInstance;
    }

    function toggleDataset(toggle) {
        var id = toggle.dataset.target;
        var action = toggle.dataset.action;
        var index = parseInt(toggle.dataset.dataset);

        var chart = document.querySelector(id);
        var chartInstance = getChartInstance(chart);

        // Action: Toggle
        if (action === 'toggle') {
            var datasets = chartInstance.data.datasets;

            var activeDataset = datasets.filter(function (dataset) {
                return !dataset.hidden;
            })[0];

            var backupDataset = datasets.filter(function (dataset) {
                return dataset.order === 1000;
            })[0];

            // Backup active dataset
            if (!backupDataset) {
                backupDataset = {};

                for (var prop in activeDataset) {
                    if (prop !== '_meta') {
                        backupDataset[prop] = activeDataset[prop];
                    }
                }

                backupDataset.order = 1000;
                backupDataset.hidden = true;

                // Push to the dataset list
                datasets.push(backupDataset);
            }

            // Toggle dataset
            var sourceDataset = (datasets[index] === activeDataset) ? backupDataset : datasets[index];

            for (var prop in activeDataset) {
                if (prop !== '_meta') {
                    activeDataset[prop] = sourceDataset[prop];
                }
            }

            // Update chart
            chartInstance.update();
        }

        // Action: Add
        if (action === 'add') {
            var dataset = chartInstance.data.datasets[index];
            var isHidden = dataset.hidden;

            // Toggle dataset
            dataset.hidden = !isHidden;
        }

        // Update chart
        chartInstance.update();
    }

    function toggleLegend(legend) {
        var chart = getChartInstance(legend);
        var content = chart.generateLegend();

        var id = legend.dataset.target;
        var container = document.querySelector(id);

        container.innerHTML = content;
    }

    //
    // Events
    //

    if (typeof Chart !== 'undefined') {

        // Global options
        globalOptions();

        // Toggle dataset
        if (toggles) {
            [].forEach.call(toggles, function (toggle) {
                var event = toggle.dataset.trigger;

                toggle.addEventListener(event, function () {
                    toggleDataset(toggle);
                });

            });
        }

        // Toggle legend
        if (legends) {
            document.addEventListener('DOMContentLoaded', function () {
                [].forEach.call(legends, function (legend) {
                    toggleLegend(legend);
                });
            });
        }
    }
})();

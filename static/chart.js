document.addEventListener('DOMContentLoaded', () => {
    const socket = io.connect('http://' + document.domain + ':' + location.port);

    // チャートの初期化
    let chart = null;

    // チャートの更新関数
    function updateChart(labels, data) {
        if (!chart) {
            const ctx = document.getElementById('stockChart').getContext('2d');
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Stock Price',
                        data: data,
                        borderColor: 'blue',
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        xAxes: [{
                            type: 'time',
                            time: {
                                unit: 'minute'
                            },
                            distribution: 'linear'
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: false
                            
                        }]
                    }
                }
            });
        } else {
            chart.data.labels = labels;
            chart.data.datasets.forEach((dataset) => {
                dataset.data = data;
            });
            chart.update();
        }
    }

    // サーバから株価データを受信してチャートを更新
    socket.on('update_stock_prices', data => {
        const labels = data.map(item => new Date());
        const stockPrices = data.map(item => item.stock_price);
        updateChart(labels, stockPrices);
    });
});

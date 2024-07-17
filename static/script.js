// SocketIOを使用してリアルタイムで株価とイベントを更新
document.addEventListener('DOMContentLoaded', () => {
    const socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('update_stock_price', data => {
        const companyElement = document.getElementById(`company_${data.company_id}`);
        if (companyElement) {
            companyElement.innerHTML = data.new_price.toFixed(2);
        }
    });

    socket.on('update_event', data => {
        const eventElement = document.getElementById('events');
        if (eventElement) {
            const newEvent = document.createElement('li');
            newEvent.textContent = `${data.event_name} - Impact: ${data.effect.toFixed(2)}`;
            eventElement.appendChild(newEvent);
        }
    });
});

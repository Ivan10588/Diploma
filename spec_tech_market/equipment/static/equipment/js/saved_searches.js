function toggleNotification(searchId, isChecked) {
    fetch(`/equipment/api/toggle-notification/${searchId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({notify: isChecked})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка сети');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'updated') {
            showNotification('Настройки уведомлений обновлены', 'success');
        } else {
            showNotification('Ошибка при обновлении уведомлений', 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showNotification('Произошла ошибка сети', 'error');
    });
}

function deleteSearch(searchId) {
    if (confirm('Удалить этот сохранённый поиск?')) {
        fetch(`/equipment/api/delete-search/${searchId}/`, {
            method: 'DELETE',
            headers: {'X-CSRFToken': getCsrfToken()}
        })
        .then(response => {
            if (response.status === 204) {
                showNotification('Поиск удалён', 'success');
                location.reload();
            } else {
                throw new Error('Ошибка сервера');
            }
        })
        .catch(error => {
            console.error('Ошибка удаления:', error);
            showNotification('Ошибка при удалении поиска', 'error');
        });
    }
}

function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : null;
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

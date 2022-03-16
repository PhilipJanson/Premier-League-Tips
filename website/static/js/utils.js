function deleteTip(tipId) {
    fetch('/delete-tip', {
        method: "POST",
        body: JSON.stringify({ tip_id : tipId}),
    }).then((_res) => {
        window.location.href = "/fixtures";
    });
}

function loadTips() {
    fetch('/load-tips', {
        method: "POST",
        body: JSON.stringify(),
    }).then((_res) => {
        window.location.href = "/admin";
    });
}
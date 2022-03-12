function deleteTip(tipId) {
    fetch('/delete-tip', {
        method: "POST",
        body: JSON.stringify({ tip_id : tipId}),
    }).then((_res) => {
        window.location.href = "/fixtures";
    });
}
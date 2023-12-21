var modal = document.getElementById("myModal");
var btn = document.getElementById("openModalBtn");
var span = document.getElementsByClassName("close")[0];
btn.onclick = function () {
    modal.style.display = "block"
}
span.onclick = function () {
    modal.style.display = "none"
}
window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
function toggleSelectAll() {
    var items = document.getElementsByName('ids');
    var allChecked = true;

    // 检查是否所有复选框都已选中
    for (var i = 0; i < items.length; i++) {
        if (items[i].type == 'checkbox' && !items[i].checked) {
            allChecked = false;
            break;
        }
    }

    // 根据当前状态切换选中或取消选中
    for (var i = 0; i < items.length; i++) {
        if (items[i].type == 'checkbox') {
            items[i].checked = !allChecked;
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
  let popup = document.getElementById('popup-message');
  if (popup) {
    popup.style.display = 'block';
    setTimeout(function() {
      popup.style.display = 'none';
    }, 3000); // 将 3000 更改为您希望弹窗显示的毫秒数
  }
});
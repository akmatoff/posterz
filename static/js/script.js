const deleteForm = document.getElementById('delete-form');
const dropdownContent = document.getElementById('dropdown-content');
const dropdownButton = document.getElementById('dropdown-button');


if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
  dropdownButton.addEventListener('touchstart', showDropdownContent)
}
dropdownButton.addEventListener('click', showDropdownContent)

// Confirm article deletion
function deleteArticleWarning() {
    var deleteWarning = confirm("Вы действительно хотите удалить статью?");

    if (deleteWarning === false) {
        deleteForm.removeAttribute('action');
    }
}

// Show dropdown
function showDropdownContent() {
  if (dropdownContent.style.display === 'none') {
    dropdownContent.style.display = 'flex';
  } else {
    dropdownContent.style.display = 'none';
  }
}

function closeDropdown() {
  dropdownContent.style.display = 'none';
  console.log('pressed');
}

// document.addEventListener('mousedown', closeDropdown)


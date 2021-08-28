// Get the search input and times icon elements
var searchInput = document.getElementById("search-input");
var timesIcon = document.getElementById("times-icon");

// Get length of string in input
var searchLength = searchInput.value.length;

// Hide/unhide times icon if searchLength is zero/non-zero
searchInput.addEventListener("input", function () {
	if (this.value.length > 0) {
		timesIcon.style.visibility = "visible";
	} else if (this.value.length == 0) {
		timesIcon.style.visibility = "hidden";
	}
});

// Clear input when timesIcon is pressed
timesIcon.addEventListener("click", function () {
	searchInput.value = "";
	searchInput.focus();
	timesIcon.style.visibility = "hidden";
});

// Get form group
var formGroup = document.getElementsByClassName("form-group").item(0);

// Add box shadow when input focused
searchInput.addEventListener("focus", function () {
	formGroup.style.boxShadow = "0px 2px 4px 2px rgba(0, 0, 0, 0.1)";
});

// Remove box shadow when input out of focus
searchInput.addEventListener("focusout", function () {
	formGroup.style.boxShadow = "none";
});

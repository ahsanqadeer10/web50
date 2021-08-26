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
});

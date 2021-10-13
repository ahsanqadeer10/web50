document.addEventListener("DOMContentLoaded", function () {
	const url_name = JSON.parse(document.getElementById("url_name").textContent);
	activate_header_link(url_name);
	if (url_name == "profile") {
		on_profile_load();
	}
});

function on_profile_load() {
	var follow_toggle = document.getElementById("follow-toggle");
	if (follow_toggle !== null) {
		follow_toggle.onclick = function () {
			var following = follow_toggle.dataset["following"];
			fetch(`${window.location.pathname}/follow_toggle`, {
				method: "PUT",
				body: JSON.stringify({
					following: following,
				}),
			})
				.then((response) => response.json())
				.then((results) => {
					follow_toggle.dataset["following"] = results["following"];
					follow_toggle.innerText =
						results["following"] == "true" ? "Unfollow" : "Follow";
					document.getElementById("followers-count").innerText =
						results["followers_count"];
				});
		};
	}
}

function activate_header_link(url_name) {
	header_links = document.getElementsByClassName("header-link");
	header_links_auth = document.getElementsByClassName("header-link-auth");
	links = Array.from(header_links).concat(Array.from(header_links_auth));
	for (var i = 0; i < links.length; i++) {
		if (links[i].dataset["url"] == url_name) {
			links[i].classList.add("active-header-link");
		} else {
			links[i].classList.remove("active-header-link");
		}
	}
}

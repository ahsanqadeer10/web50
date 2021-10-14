Element.prototype.setAttributes = function (attributes) {
	for (var key in attributes) {
		if (
			(key === "styles" || key === "style") &&
			typeof attributes[key] === "object"
		) {
			for (var property in attributes[key]) {
				this.style.property = attributes[key][property];
			}
		} else if (key === "html") {
			this.innerHTML = attributes[key];
		} else {
			this.setAttribute(key, attributes[key]);
		}
	}
};

function getCookie(name) {
	const value = `; ${document.cookie}`;
	const parts = value.split(`; ${name}=`);
	if (parts.length === 2) return parts.pop().split(";").shift();
}

document.addEventListener("DOMContentLoaded", function () {
	const url_name = JSON.parse(document.getElementById("url_name").textContent);
	activate_header_link(url_name);
	if (url_name == "index") {
		on_index_load();
	} else if (url_name == "profile") {
		on_profile_load();
	}
});

function on_index_load() {
	setupPostEditMechanism();
}

function on_profile_load() {
	setupPostEditMechanism();
	setupFollowMechanism();
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

function setupFollowMechanism() {
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
					results["following"] == "true"
						? follow_toggle.classList.add("follow-toggle-true")
						: follow_toggle.classList.remove("follow-toggle-true");
					document.getElementById("followers-count").innerText =
						results["followers_count"];
				});
		};
	}
}

function setupPostEditMechanism() {
	// define a variable that checks if anything is being edited currently
	var editing = null;

	handle_edit_event();
	// for each edit button on any post

	function handle_edit_event() {
		document
			.querySelectorAll(".post-card .edit-btns .edit")
			.forEach((edit_button) => {
				// add an onclick handler that replaces the content with textarea and replaces the edit button with save and cancel buttons
				edit_button.onclick = () => {
					if (editing !== null) {
						console.log(`${editing} is being edited!`);
						return;
					}

					post_elem = edit_button.parentNode.parentNode;
					post_id = post_elem.dataset["post_id"];

					content_elem = post_elem.getElementsByClassName("content")[0];
					initial_content = content_elem.innerText;

					// create text area element
					textarea_elem = document.createElement("div");
					textarea = document.createElement("textarea");
					textarea.setAttributes({
						name: "content",
						rows: "2",
					});
					textarea.value = initial_content;
					textarea_elem.appendChild(textarea);

					// replace content with textarea
					post_elem.replaceChild(textarea_elem, content_elem);
					textarea.focus();

					// create save and cancel buttons
					save_button = document.createElement("button");
					save_button.innerHTML = "Save";
					save_button.classList.add("save");
					cancel_button = document.createElement("button");
					cancel_button.innerHTML = "Cancel";
					cancel_button.classList.add("cancel");

					// replace edit with save and cancel buttons
					edit_button.hidden = true;
					edit_button.parentNode.appendChild(save_button);
					edit_button.parentNode.appendChild(cancel_button);

					editing = post_id;

					handle_cancel_event(edit_button);
					handle_save_event(edit_button);
				};
			});
	}

	function handle_cancel_event(edit_button) {
		cancel_button.onclick = () => {
			// replace textarea with content
			post_elem.replaceChild(content_elem, textarea_elem);

			// replace edit and save buttons with edit button
			save_button.remove();
			cancel_button.remove();
			edit_button.hidden = false;

			editing = null;
		};
	}

	function handle_save_event(edit_button) {
		save_button.onclick = () => {
			// get textarea value
			modified_content = textarea.value;
			if (modified_content === initial_content) {
				console.log("No changes made. Please make changes to save.");
				textarea.focus();
			} else if (modified_content === "") {
				console.log("Empty post. Please write something.");
				textarea.focus();
			} else {
				// update post's content
				fetch(`/post/${post_id}/edit`, {
					method: "PUT",
					body: JSON.stringify({
						modified_content: modified_content,
					}),
					credentials: "same-origin",
					headers: {
						"X-CSRFToken": getCookie("csrftoken"),
					},
				})
					.then((response) => response.json())
					.then((results) => {
						// if the update process is successful
						if (results.message === "success") {
							// replace content with modified content
							content_elem.innerText = modified_content;

							// replace textarea with content
							post_elem.replaceChild(content_elem, textarea_elem);

							// replace edit and save buttons with edit button
							save_button.remove();
							cancel_button.remove();
							edit_button.hidden = false;

							editing = null;
						}
					});
			}
		};
	}
}

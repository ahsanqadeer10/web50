// Create function on DOM element to assign multiple attributes at once
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

function auto_resize_textarea() {
	document.querySelectorAll("textarea").forEach((textarea) => {
		textarea.style.height = textarea.scrollHeight + "px";
		textarea.style.overflowY = "hidden";
		textarea.oninput = on_input;
	});

	function on_input() {
		this.style.height = "auto";
		this.style.height = this.scrollHeight + "px";
	}
}

// Create function to get cookie (for csrf validation)
function get_cookie(name) {
	const value = `; ${document.cookie}`;
	const parts = value.split(`; ${name}=`);
	if (parts.length === 2) return parts.pop().split(";").shift();
}

// Run this when the DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
	const url_name = JSON.parse(document.querySelector("#url_name").textContent);
	activate_header_link(url_name);
	if (url_name == "index") {
		on_index_load();
	} else if (url_name == "profile") {
		on_profile_load();
	} else if (url_name == "following") {
		on_following_load();
	} else if (url_name == "register") {
		on_register_load();
	}

	function activate_header_link(url_name) {
		links = document.querySelectorAll("header nav a");
		links.forEach((link) => {
			if (link.dataset["url"] == url_name) {
				link.classList.add("active");
			} else {
				link.classList.remove("active");
			}
		});
	}

	function on_index_load() {
		auto_resize_textarea();
		setup_post_edit_mechanism();
		setup_post_like_mechanism();
		setup_post_delete_mechanism();
	}

	function on_profile_load() {
		setup_post_edit_mechanism();
		setup_follow_mechanism();
		setup_post_like_mechanism();
		setup_post_delete_mechanism();
	}

	function on_following_load() {
		setup_post_like_mechanism();
	}

	function on_register_load() {
		preview_image();
	}
});

function setup_follow_mechanism() {
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

function setup_post_edit_mechanism() {
	// define a variable that checks if anything is being edited currently
	var editing = false;
	var post_elem = null;
	var initial_content = null;

	edit_buttons = document.querySelectorAll(".post-author-buttons .edit");
	edit_buttons.forEach((edit_button) => {
		edit_button.onclick = () => {
			if (editing === true) {
				console.log(`Something is being edited!`);
				return;
			}
			post_elem = edit_button.parentNode.parentNode.parentNode;
			display_editing_area();
		};
	});

	function display_editing_area() {
		content_elem = post_elem.querySelector(".post-content");
		initial_content = content_elem.innerText;

		// create text area element
		textarea = document.createElement("textarea");
		textarea.value = initial_content;
		textarea_elem = document.createElement("div");
		textarea_elem.classList.add("post-content-edit");
		textarea_elem.appendChild(textarea);

		post_elem.replaceChild(textarea_elem, content_elem);
		auto_resize_textarea();
		textarea.focus();

		// create save and cancel buttons
		save_button = document.createElement("button");
		save_button.innerHTML = "Save";
		save_button.classList.add("save");
		save_button.onclick = save_button_pressed;
		cancel_button = document.createElement("button");
		cancel_button.innerHTML = "Cancel";
		cancel_button.classList.add("cancel");
		cancel_button.onclick = cancel_button_pressed;

		// replace edit with save and cancel buttons
		post_buttons = post_elem.querySelector(".post-author-buttons");
		post_buttons.querySelector(".edit").hidden = true;
		post_buttons.querySelector(".remove").hidden = true;
		post_buttons.appendChild(save_button);
		post_buttons.appendChild(cancel_button);

		editing = true;
	}

	function cancel_button_pressed() {
		if (editing !== true || post_elem === null || initial_content === null) {
			console.log("Something is wrong. Cannot cancel.");
			return;
		}
		close_editing_area(initial_content);
	}

	function save_button_pressed() {
		if (editing !== true || post_elem === null || initial_content === null) {
			console.log("Something is wrong. Cannot cancel.");
			return;
		}

		var modified_content = post_elem.querySelector("textarea").value;

		if (modified_content === initial_content) {
			console.log("No changes made. Please make changes to save.");
			textarea.focus();
			return;
		} else if (modified_content === "") {
			console.log("Empty post. Please write something.");
			textarea.focus();
			return;
		}

		fetch(`/post/${post_elem.dataset["post_id"]}/edit`, {
			method: "PUT",
			body: JSON.stringify({
				modified_content: modified_content,
			}),
			credentials: "same-origin",
			headers: {
				"X-CSRFToken": get_cookie("csrftoken"),
			},
		})
			.then((response) => response.json())
			.then((results) => {
				// if the update process is successful
				if (results.message === "success") {
					close_editing_area(modified_content);
				}
			});
	}

	function close_editing_area(content) {
		// create content element
		content_elem = document.createElement("div");
		content_elem.classList.add("post-content");
		content_elem.innerText = content;

		post_elem.replaceChild(content_elem, textarea_elem);

		// replace edit and save buttons with edit button
		post_buttons = post_elem.querySelector(".post-author-buttons");
		post_buttons.querySelector(".save").remove();
		post_buttons.querySelector(".cancel").remove();
		post_buttons.querySelector(".edit").hidden = false;
		post_buttons.querySelector(".remove").hidden = false;

		editing = false;
		post_elem = null;
		intial_content = null;
	}
}

function setup_post_like_mechanism() {
	post_elem = null;

	like_buttons = document.querySelectorAll(".like");
	like_buttons.forEach((button) => {
		button.onclick = () => {
			post_elem = button.parentNode.parentNode;
			switch (button.dataset["toggle"]) {
				case "true":
					like_post();
					break;
				case "false":
					unlike_post();
					break;
				default:
					break;
			}
		};
	});

	function like_post() {
		if (post_elem == null) {
			console.log("Something is wrong. Cannot like post.");
			return;
		}

		fetch(`/post/${post_elem.dataset["post_id"]}/like`, {
			method: "PUT",
			credentials: "same-origin",
			headers: {
				"X-CSRFToken": get_cookie("csrftoken"),
			},
		})
			.then((response) => response.json())
			.then((results) => {
				if (results.message == "success") {
					change_toggle(false);
					change_like_count(results.like_count);
				}
			});
	}

	function unlike_post() {
		if (post_elem == null) {
			console.log("Something is wrong. Cannot like post.");
			return;
		}

		fetch(`/post/${post_elem.dataset["post_id"]}/unlike`, {
			method: "PUT",
			credentials: "same-origin",
			headers: {
				"X-CSRFToken": get_cookie("csrftoken"),
			},
		})
			.then((response) => response.json())
			.then((results) => {
				if (results.message == "success") {
					change_toggle(true);
					change_like_count(results.like_count);
				}
			});
	}

	function change_toggle(toggle_data) {
		button = post_elem.querySelector(".like");
		if (toggle_data == true) {
			button.dataset["toggle"] = "true";
			button.innerText = "Like";
		} else if (toggle_data == false) {
			button.dataset["toggle"] = "false";
			button.innerText = "Liked!";
		}
		button.blur();
	}

	function change_like_count(count) {
		if (count > 0) {
			post_elem.querySelector(
				".post-likes"
			).innerHTML = `<i class="bi bi-hand-thumbs-up-fill"></i> Liked by ${count}!`;
		} else {
			post_elem.querySelector(".post-likes").innerText = "";
		}
	}
}

function setup_post_delete_mechanism() {
	post_elem = null;

	document.querySelectorAll(".post-buttons .remove").forEach((button) => {
		button.onclick = () => {
			console.log("Remove button clicked!");
			post_elem = button.parentNode.parentNode;
			take_confirmation();
		};
	});

	function take_confirmation() {
		var modal = bootstrap.Modal.getInstance($("#remove-post-modal"));
		document.onclick = () => {
			if (this.event.target.id == "remove-confirm") {
				delete_post();
			}
		};
	}

	function delete_post() {
		fetch(`/post/${post_elem.dataset["post_id"]}/delete`, {
			method: "DELETE",
			credentials: "same-origin",
			headers: {
				"X-CSRFToken": get_cookie("csrftoken"),
			},
		})
			.then((response) => response.json())
			.then((results) => {
				if (results.message == "success") {
					console.log("Successully deleted post!");
					$("#remove-post-modal").hide();
					location.reload();
				}
			});
	}
}

function preview_image() {
	const default_image_url = "../../../media/images/default-profile-pic.png";
	var image = document.querySelector("#preview-image");
	preview_displayed = false;

	document.querySelector("#profile-picture").onchange = function () {
		if (this.files && this.files[0]) {
			show_preview(this.files[0]);
			this.blur();
		}
	};

	function show_preview(img_data) {
		var img_url = URL.createObjectURL(img_data);
		image.src = img_url;

		if (preview_displayed == false) {
			remove_image_button = document.createElement("a");
			remove_image_button.innerHTML = `Remove`;
			remove_image_button.classList.add("remove");
			remove_image_button.onclick = remove_image;

			image.parentNode.parentNode.appendChild(remove_image_button);

			preview_displayed = true;
		}
	}

	function remove_image() {
		image.src = default_image_url;
		preview_displayed = false;
		image.parentNode.parentNode.querySelector(".remove").remove();
	}
}

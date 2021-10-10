document.addEventListener("DOMContentLoaded", function () {
	// Use buttons to toggle between views
	document
		.querySelector("#inbox")
		.addEventListener("click", () => load_mailbox("inbox"));
	document
		.querySelector("#sent")
		.addEventListener("click", () => load_mailbox("sent"));
	document
		.querySelector("#archived")
		.addEventListener("click", () => load_mailbox("archive"));
	document.querySelector("#compose").addEventListener("click", compose_email);
	document.querySelector("#compose-form").onsubmit = send_email;

	// By default, load the inbox
	load_mailbox("inbox");
});

function compose_email() {
	// Show compose view and hide other views
	document.querySelector("#emails-view").style.display = "none";
	document.querySelector("#email-view").style.display = "none";
	document.querySelector("#compose-view").style.display = "block";

	// Clear out composition fields
	document.querySelector("#compose-recipients").value = "";
	document.querySelector("#compose-subject").value = "";
	document.querySelector("#compose-body").value = "";
	document.querySelector("#parent-id").value = -1;
}

function send_email() {
	const recipients = document.querySelector("#compose-recipients").value;
	const subject = document.querySelector("#compose-subject").value;
	const body = document.querySelector("#compose-body").value;
	const parent_id = document.querySelector("#parent-id").value;
	fetch("/emails", {
		method: "POST",
		body: JSON.stringify({
			recipients: recipients,
			subject: subject,
			body: body,
			parent_id: parseInt(parent_id),
		}),
	})
		.then((response) => response.json())
		.then((result) => {
			if (result.error) {
				console.log(result.error);
			} else {
				load_mailbox("sent");
			}
		});

	return false;
}

function mark_as_read(email_id) {
	fetch(`emails/${email_id}`, {
		method: "PUT",
		body: JSON.stringify({
			read: true,
		}),
	}).then((response) => {
		if (response.status === 204) {
			return;
		}
	});
}

function toggle_archive(email) {
	fetch(`emails/${email.id}`, {
		method: "PUT",
		body: JSON.stringify({
			archived: email.archived === false ? true : false,
		}),
	}).then((response) => {
		if (response.status === 204) {
			load_mailbox("inbox");
		}
	});
}

function load_email_element(email) {
	document.querySelector("#email-subject").innerHTML =
		email.subject === "" ? "No Subject" : email.subject;
	document.querySelector("#email-sender").innerHTML = email.sender;
	document.querySelector("#email-recipients").innerHTML = email.recipients;
	document.querySelector("#email-timestamp").innerHTML = email.timestamp;
	document.querySelector("#email-body").style.whiteSpace = "pre-wrap";
	document.querySelector("#email-body").innerHTML = email.body;
	const user_email = JSON.parse(document.getElementById("user_id").textContent);
	if (user_email !== email.sender) {
		const archive_toggle = document.querySelector("#archive_toggle");
		archive_toggle.style.display = "block";
		archive_toggle.innerHTML =
			email.archived === false ? "Archive" : "Un-archive";
		archive_toggle.onclick = function () {
			toggle_archive(email);
		};
	} else {
		archive_toggle.style.display = "none";
	}
	document
		.querySelector("#compose-reply")
		.addEventListener("click", function () {
			compose_reply(email);
		});
}

function load_email(email_id) {
	document.querySelector("#emails-view").style.display = "none";
	document.querySelector("#email-view").style.display = "block";

	fetch(`emails/${email_id}`)
		.then((response) => response.json())
		.then((email) => {
			console.log(email);
			console.log(email.parent);
			load_email_element(email);
			if (!email.read) {
				mark_as_read(email.id);
			}
		});
}

function load_mailbox_element(mailbox, emails) {
	emails.forEach(function (email) {
		const element = document.createElement("div");
		element.classList.add("email");
		if (email.read) {
			element.classList.add("read");
		}
		if (mailbox === "sent") {
			const recipients = document.createElement("div");
			recipients.innerHTML = email.recipients;
			element.append(recipients);
		} else {
			const sender = document.createElement("div");
			sender.innerHTML = email.sender;
			element.append(sender);
		}
		const subject = document.createElement("div");
		subject.innerHTML = email.subject === "" ? "No Subject" : email.subject;
		element.append(subject);
		const timestamp = document.createElement("div");
		timestamp.innerHTML = email.timestamp;
		element.append(timestamp);

		element.addEventListener("click", function () {
			load_email(email.id);
		});

		document.querySelector("#emails-view").append(element);
	});
}

function load_mailbox(mailbox) {
	// Show the mailbox and hide other views
	document.querySelector("#emails-view").style.display = "block";
	document.querySelector("#email-view").style.display = "none";
	document.querySelector("#compose-view").style.display = "none";

	// Show the mailbox name
	document.querySelector("#emails-view").innerHTML = `<h3>${
		mailbox.charAt(0).toUpperCase() + mailbox.slice(1)
	}</h3>`;

	// Fetch mailbox emails
	fetch(`/emails/${mailbox}`)
		.then((response) => response.json())
		.then((emails) => load_mailbox_element(mailbox, emails));
}

function compose_reply(email) {
	// Show compose view and hide other views
	document.querySelector("#email-view").style.display = "none";
	document.querySelector("#compose-view").style.display = "block";

	// Clear out composition fields
	document.querySelector("#compose-recipients").value = email.sender;
	document.querySelector("#compose-recipients").disabled = true;
	if (email.subject.startsWith("Re: ") === true) {
		document.querySelector("#compose-subject").value = email.subject;
	} else {
		document.querySelector("#compose-subject").value = `Re: ${email.subject}`;
	}

	body_prefix = `On ${email.timestamp} ${email.sender} wrote: \n ${email.body} \n`;
	seperator = "--------------------";
	document.querySelector(
		"#compose-body"
	).value = `${body_prefix} \n ${seperator} \n \n`;
	document.querySelector("#compose-body").focus();
	document.querySelector("#parent-id").value = email.id;
}

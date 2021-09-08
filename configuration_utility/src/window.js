$(() => {

	const ForescoutAPI = require('./forescout-api');
	const selectedFields = {};
	const selectedItems = {};
	let hostMap = {};
	let timeouts = {};
	let hostFields = [];

	async function initializeAPI() {
		const apiEndpoint = $('#apiEndpoint').val();
		const username = $('#username').val();
		const password = $('#password').val();

		try {
			showLoader();
			await ForescoutAPI.configure(apiEndpoint, username, password);

			localStorage.setItem('apiEndpoint', apiEndpoint);
			localStorage.setItem('username', username);
			hideLoginScreen();
			showConfigScreen();
		} catch (error) {
			hideLoader();
			console.error(error);
			alert(error.message);
		}
	}

	function showLoginScreen() {

	}

	function hideLoginScreen() {
		$("#loginScreen").hide();
	}

	function onItemDblClick(e) {
		if (event.target == event.currentTarget) {
			e.stopPropagation();
			const item = $(e.target);
			if (item.hasClass('active')) {
				return;
			}

			const name = e.target.dataset.name;
			const field = hostMap[name];

			const selected = selectedFields[name];

			if (!selected) {
				selectedFields[name] = field;
				item.addClass('active');
			}

			renderSelection();
			renderString();
		}
	}

	function onFilterList(listName, text) {
		if (timeouts[listName]) {
			clearTimeout(timeouts[listName]);
		}

		timeouts[listName] = setTimeout(() => {
			const list = $(`#${listName}`);
			const regex = new RegExp(`.*${text}.*`, 'i');

			list.children().each(function () {
				if (!text) {
					this.style.display = "block";
				} else {
					if (regex.test(this.dataset.name) || regex.test(this.dataset.label)) {
						this.style.display = "block";
					} else {
						this.style.display = "none";
					}
				}
			});
		}, 300);
	}

	function onEditName(field, e) {
		field.newName = e.target.value;
		renderString();
	}

	function onX(field, e) {
		delete selectedFields[field.name];

		showLoader();

		setTimeout(() => {
			renderHostfields();
			renderSelection();
			renderString();

			const filterHosts = $("#filterHostList").val();
			const filterSelected = $("#filterSelectedList").val();

			if (filterHosts) {
				onFilterList('hostfieldList', filterHosts)
			}

			if (filterSelected) {
				onFilterList('selectedList', filterSelected);
			}
			hideLoader();
		}, 50);
	}

	function renderHostfields() {
		const list = $("#hostfieldList");
		list.html('');

		for (const field of hostFields) {
			const item = $(`<div class='list-group-item list-group-item-action' data-name='${field.name}' data-label='${field.label}'>`);
			item.dblclick(onItemDblClick.bind(this));
			item.html(`<div style='pointer-events: none;'>${field.label} <small>(${field.name})</small></div><div style='pointer-events: none;'><small style='pointer-events: none;'>${field.description}</small></div>`);
			list.append(item);

			if (selectedFields[field.name]) {
				item.addClass('active');
			}
		}
	}

	function renderSelection() {
		const list = $("#selectedList");
		list.html("");

		for (const name in selectedFields) {
			const field = selectedFields[name];
			const item = $(`<div class='list-group-item list-group-item-action' data-name='${field.name}' data-label='${field.label}' title='${field.description}'>`);
			item.dblclick(onItemDblClick.bind(this));
			item.html(`
				<div style='pointer-events: none;'>${field.label} <small>(${field.name})</small></div>
				<div style='padding: 10px 0px;'><small>Name: <input type="text" value="${field.newName || field.name}" style="width: 90%;"/></small></div>
				<button class="btn btn-outline-danger X">X</button>
			`);
			const input = item.find('input');
			input.bind('keyup', function(e){
				onEditName(field, e);
			});

			const button = item.find('button');
			button.click(function () {
				onX(field);
			})
			list.append(item);
		}
	}

	function renderString() {
		const html = $("#string");
		html.html('');
		let str = [];

		for (const name in selectedFields) {
			const field = selectedFields[name];
			str.push(`${name}(${field.newName || field.name})`);
		}

		html.html(str.join(',<br/>'));
	}

	async function showConfigScreen() {
		try {
			hostFields = await ForescoutAPI.getHostfields();
			hostFields = hostFields.sort((a, b) => {
				return a.label < b.label ? -1 : 1;
			})

			hostMap = hostFields.reduce((acc, field) => {
				acc[field.name] = field;
				return acc;
			}, {});

			renderHostfields();

			$("#configScreen").show();
		} catch (error) {
			console.error(error);
			alert(error.message);
		} finally {
			hideLoader();
		}
	}

	function showLoader() {
		$("#loader").show();
	}

	function hideLoader() {
		$("#loader").hide();
	}

	(function bindHandlers() {
		$('#buttonForescoutConnect').click(initializeAPI.bind(this));
		$('#loginForm').submit(initializeAPI.bind(this));
		$('#filterHostList').bind('keyup', function (event) {
			onFilterList('hostfieldList', event.target.value);
		});
		$('#filterSelectedList').bind('keyup', function (event) {
			onFilterList('selectedList', event.target.value);
		});
	})();

	(function loadPreviousValues() {
		$('#apiEndpoint').val(localStorage.getItem('apiEndpoint') || '');
		$('#username').val(localStorage.getItem('username') || '');
	})();
});

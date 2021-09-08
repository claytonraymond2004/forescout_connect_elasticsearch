const { app, BrowserWindow } = require('electron')
const path = require('path')
const url = require('url')

let window = null

app.once('ready', () => {
	window = new BrowserWindow({
		width: 1024,
		height: 900,
		backgroundColor: "#ffffff",
		show: false,
		webPreferences: {
			nodeIntegration: true,

		}
	});

	window.loadURL(url.format({
		pathname: path.join(__dirname, 'window.html'),
		protocol: 'file:',
		slashes: true
	}));

	window.once('ready-to-show', () => {
		window.maximize();
		window.show();
	});
})
const axios = require('axios');
const DEFAULT_REQUEST_TIMEOUT = 60000;

class ForescoutAPI {
	constructor() {
	}

	async configure(apiEndpoint, username, password) {
		this.apiEndpoint = apiEndpoint;
		this.username = username;
		this.password = password;

		if (!this.axios) {
			this.axios = axios.create({
				timeout: DEFAULT_REQUEST_TIMEOUT,
				baseURL: this.apiEndpoint
			});
		}

		if (apiEndpoint) {
			this.apiEndpoint = apiEndpoint;
			this.axios.defaults.baseURL = this.apiEndpoint;
		}

		if (username && password) {
			this.apiToken = await this.login(username, password);
		}

		if (!this.apiToken) {
			throw new Error('Login failed.');
		}
	}

	async login(){
		if (this.username && this.password) {
			const response = await this.axios.post('/api/login', null, {
				params: {
					username: this.username,
					password: this.password
				}
			});

			this.apiToken = response.data
			this.axios.defaults.headers.common['Authorization'] = this.apiToken;
		}

		return this.apiToken;
	}

	async getHostfields() {
		return (await this.axios.get('/api/hostfields')).data.hostFields;
	}
}

module.exports = new ForescoutAPI();
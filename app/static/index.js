
const url = "/rand";

const vuetify = new Vuetify({
	icons: {
		iconfont: 'mdi'
	}
})

const vm = new Vue({ // vm is our Vue instance's name for consistency.
	el: '#vm',
	vuetify: new Vuetify(),
	delimiters: ['[[', ']]'],
	data: () => ({
		greeting: 'Hello, Vue!',
		results: [],
		snackbar: false,
		status_text: ``,
		search: null,
		source: null,
		show: true,
		news: null,
		categories: [],
		category: [],
		datemenu: false,
		dates: ['2022-01-01', new Date().toISOString().slice(0, 10)],
		menu: false,
		modal: false,
		unread_switch: true,
        important_switch: false,
		menu2: false,
	}),
	methods: {
		created() {
			this.getMessage();
		},
		ignoreSource: function (event) {
			const source = this.source[0][0];
			axios
				.get("/ignore_source?source=" + source)
				.then(function (response) {
					if (response.status == 200) {
						vm.snackbar = true;
						vm.status_text = "Ignored Source: " + source;
					}
				})
				.catch((error) => {
					// eslint-disable-next-line
					console.error(error);
					vm.snack_failure();
				});
			event.preventDefault();
			event.stopPropagation();

		},
		update: function (event) {
			axios
				.get("/update")
				.then(function (response) {
					if (response.status == 200) {
						vm.snackbar = true;
						vm.status_text = "Update Success!";
						axios
							.get("/getnews?important=" + vm.important_switch + "&unread=" + vm.unread_switch + "&min_date=" + vm.dates[0] + "&max_date=" + vm.dates[1])
							.then(response => (vm.news = response.data));
					}
				})
				.catch((error) => {
					// eslint-disable-next-line
					console.error(error);
					vm.snack_failure();
				});
			event.preventDefault();
			event.stopPropagation();
		},
		favouriteSource: function (event) {
			const source = this.source[0][0];
			axios
				.get("/favourite_source?source=" + source)
				.then(function (response) {
					if (response.status == 200) {
						vm.snackbar = true;
						vm.status_text = "Favourited Source: " + source;
					}c
				})
				.catch((error) => {
					// eslint-disable-next-line
					console.error(error);
					vm.snack_failure();
				});
			event.preventDefault();
			event.stopPropagation();
		},
		mark_important: function (event) {
			console.log(this.link);
			const link = this.link[0][0];
			axios
				.get("/mark_important?link=" + link)
				.then(function (response) {
					if (response.status == 200) {
						vm.snackbar = true;
						vm.status_text = "Marked url as important: " + link;
					}
				})
				.catch((error) => {
					// eslint-disable-next-line
					console.error(error);
					vm.snack_failure();
				});
			event.preventDefault();
			event.stopPropagation();
		},
		mark_unimportant: function (event) {
			console.log(this.link);
			const link = this.link[0][0];
			axios
				.get("/mark_unimportant?link=" + link)
				.then(function (response) {
					if (response.status == 200) {
						vm.snackbar = true;
						vm.status_text = "Marked url as unimportant: " + link;
					}
				})
				.catch((error) => {
					// eslint-disable-next-line
					console.error(error);
					vm.snack_failure();
				});
			event.preventDefault();
			event.stopPropagation();
		},
		filter() {
			console.log(this.search);
			console.log(this.category);
			console.log(this.dates);
			axios
				.get("/getnews?search=" + this.search + "&important=" + this.important_switch + "&unread=" + this.unread_switch + "&categories=" + this.category + "&min_date=" + this.dates[0] + "&max_date=" + this.dates[1])
				.then(response => (this.news = response.data))
		}
	},
	mounted() {
		axios
			.get("/getnews?search=" + this.search + "&unread=" + this.unread_switch + "&important=" + this.important_switch + "&min_date=" + this.dates[0] + "&max_date=" + this.dates[1])
			.then(response => (this.news = response.data));

	},
	created() {
		axios
			.get("/feeds")
			.then(response => (this.categories = response.data));
		axios
			.get("/feeds")
			.then(response => (this.category = response.data));
	}

})


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
		results: [],
		link: null,
		snackbar: false,
		status_text: ``,
		search: null,
		source: null,
		show: true,
		news: null,
		drawer: false,
		group: null,
		limit: 50,
		categories: [],
		category: [],
		datemenu: false,
		dates: ['2022-01-01', new Date().toISOString().slice(0, 10)],
		menu: false,
		modal: false,
		unread_switch: true,
		important_switch: false,
		menu2: false,
		feeddialog: false
	}),
	methods: {
		created() {
			// this.getMessage();
		},
		update: function (event) {
			console.log("Updating feeds");
			axios
				.get("/update")
				.then(function (response) {
					if (response.status == 200) {
						vm.snackbar = true;
						vm.status_text = "Update Success!";
						axios
							.get("/getnews?limit=" + vm.limit + "&important=" + vm.important_switch + "&unread=" + vm.unread_switch + "&min_date=" + vm.dates[0] + "&max_date=" + vm.dates[1])
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
		mark_important: function (event) {
			console.log(this);
			console.log("Marking article as important: " + this.link);
			const entry_id = this.entry_id[0][0];
			const source_url = this.source_url[0][0];
			const link = this.link[0][0];
			axios
			.get("/mark_unimportant?source_url=" + source_url + "&entry_id=" + entry_id)
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
			console.log("Marking article as unimportant: " + this.link);
			const link = this.link[0][0];
			const entry_id = this.entry_id[0][0];
			const source_url = this.source_url[0][0];
			axios
				.get("/mark_unimportant?source_url=" + source_url + "&entry_id=" + entry_id)
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
			axios
				.get("/getnews?limit=" + this.limit + "&search=" + this.search + "&important=" + this.important_switch + "&unread=" + this.unread_switch + "&categories=" + this.category + "&min_date=" + this.dates[0] + "&max_date=" + this.dates[1])
				.then(response => (this.news = response.data))

		}
	},
	mounted() {
		axios
			.get("/getnews?limit=" + this.limit + "&search=" + this.search + "&unread=" + this.unread_switch + "&important=" + this.important_switch + "&min_date=" + this.dates[0] + "&max_date=" + this.dates[1])
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

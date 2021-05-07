<template>
	<v-app id="web_ui">
		<v-snackbar v-model="format_success" bottom :color="'error'" :timeout="5000">
			You have successfully deleted all data
			<br />
			From all data bases! Well Done!
			<v-icon color="yellow">
				mdi-thumb-up
			</v-icon>
			<v-btn dark text @click="snackbar = false">
				Close
			</v-btn>
		</v-snackbar>
		<vue-headful :title="currentRouteName ? 'NROS — ' + currentRouteName : 'NROS'" />

		<v-app-bar app clipped-left :absolute="currentRouteName === 'Home'" dense flat hide-on-scrol overlap :style="currentRouteName === 'Home' ? 'background: transparent' : ''">
			<v-img src="projectIconWhite.png" max-height="40" max-width="40"></v-img>

			<div class="ml-2" v-if="currentRouteName !== 'Home'">
				<v-toolbar-title link to="/dashboard">Neuro Retail Optimization System</v-toolbar-title>
			</div>

			<v-spacer></v-spacer>

			<v-tabs centered v-if="currentRouteName === 'DataChecker'">
				<v-tab link dense to="/data_checker/types">Types</v-tab>
				<v-tab link dense to="/data_checker/items">Items</v-tab>
				<v-tab link dense to="/data_checker/groups">Groups</v-tab>
				<v-tab link dense to="/data_checker/locations">Locations</v-tab>
			</v-tabs>

			<!--<v-menu absolute offset-y close-on-click transition="scale-transition">
                <template v-slot:activator="{on}">
                    <v-btn text @click.stop="notifocationsListExpanded = !notifocationsListExpanded" dark v-on="on">
                        <v-badge overlap color="green" :content="notificationBadgeNum">
                            <v-icon>mdi-bell</v-icon>
                        </v-badge>
                    </v-btn>
                </template>

                <v-list>
                    <v-list-item link dense v-for="(userMenuItem, index) in notificationItems" :key="index" router
                        :to="userMenuItem.link">
                        <v-list-item-title>{{ userMenuItem.title }}</v-list-item-title>
                    </v-list-item>
                </v-list>
            </v-menu>-->

			<v-menu v-if="isAuthenticated" offset-y close-on-click close-on-content-click v-model="userMenuExpanded">
				<template v-slot:activator="{ on }">
					<v-btn text color="red" @click.stop="userMenuExpanded = !userMenuExpanded" dark v-on="on">
						{{ currentName }}
						<v-icon right>{{ userMenuExpanded ? "mdi-menu-down" : "mdi-menu-up" }}</v-icon>
					</v-btn>
				</template>

				<v-list>
					<v-list-item link dense v-for="(notificationItem, index) in userMenuItems" :key="index" router :to="notificationItem.link">
						<v-list-item-title>{{ notificationItem.title }}</v-list-item-title>
					</v-list-item>
					<v-list-item link dense router>
						<v-list-item-title @click="formatDB" style="color: red;">Format DB</v-list-item-title>
					</v-list-item>
					<v-list-item link dense router>
						<v-list-item-title @click="logout">Log out</v-list-item-title>
					</v-list-item>
				</v-list>
			</v-menu>

			<v-btn v-else text color="red" @click="signInDialog = true">Authentication</v-btn>
		</v-app-bar>

		<v-navigation-drawer v-if="currentRouteName !== 'Home'" v-model="sidebar" hide-overlay app clipped permanent expand-on-hover floating width="200">
			<v-list dense>
				<v-list-item link dense to="/dashboard">
					<v-list-item-action>
						<v-icon>mdi-view-dashboard</v-icon>
					</v-list-item-action>
					<v-list-item-content>
						<v-list-item-title>Dashboard</v-list-item-title>
					</v-list-item-content>
				</v-list-item>
				<v-list-item link dense to="/charts">
					<v-list-item-action>
						<v-icon>mdi-chart-arc</v-icon>
					</v-list-item-action>
					<v-list-item-content>
						<v-list-item-title>Charts</v-list-item-title>
					</v-list-item-content>
				</v-list-item>
				<v-list-item link dense to="/orders">
					<v-list-item-action>
						<v-icon>mdi-clipboard-arrow-right</v-icon>
					</v-list-item-action>
					<v-list-item-content>
						<v-list-item-title>Orders</v-list-item-title>
					</v-list-item-content>
				</v-list-item>
				<v-list-item link dense to="/map">
					<v-list-item-action>
						<v-icon>mdi-map-marker-multiple</v-icon>
					</v-list-item-action>
					<v-list-item-content>
						<v-list-item-title>Map</v-list-item-title>
					</v-list-item-content>
				</v-list-item>
				<v-list-item link dense to="/data_checker">
					<v-list-item-action>
						<v-icon>mdi-database</v-icon>
					</v-list-item-action>
					<v-list-item-content>
						<v-list-item-title>Data Checker</v-list-item-title>
					</v-list-item-content>
				</v-list-item>
				<v-list-item link dense to="/settings">
					<v-list-item-action>
						<v-icon>mdi-cog-outline</v-icon>
					</v-list-item-action>
					<v-list-item-content>
						<v-list-item-title>Settings</v-list-item-title>
					</v-list-item-content>
				</v-list-item>
				<v-list-item link dense to="/help">
					<v-list-item-action>
						<v-icon>mdi-help-circle</v-icon>
					</v-list-item-action>
					<v-list-item-content>
						<v-list-item-title>Help</v-list-item-title>
					</v-list-item-content>
				</v-list-item>
				<v-list-item link dense to="/about">
					<v-list-item-action>
						<v-icon>mdi-border-all</v-icon>
					</v-list-item-action>
					<v-list-item-content>
						<v-list-item-title>About</v-list-item-title>
					</v-list-item-content>
				</v-list-item>
			</v-list>
		</v-navigation-drawer>

		<v-parallax v-if="currentRouteName === 'Home'" src="landing-image.png" height="800">
			<v-layout column align-center justify-center class="white--text">
				<h1 class="display-1 font-weight-thin mb-3">Neuro Retail Optimization System</h1>
				<h4 class="subheading">Optimize your business today</h4>
			</v-layout>
		</v-parallax>

		<v-content>
			<v-dialog v-model="signInDialog" max-width="600px">
				<v-card>
					<v-card-title>
						<span class="headline">Sign In</span>
					</v-card-title>
					<v-card-text>
						<v-container>
							<p v-if="isSignInError" class="text-center subtitle-2" style="color: red;">
								{{ signInError }}
							</p>

							<ValidationObserver ref="signInObserver">
								<form class="login">
									<ValidationProvider v-slot="{ errors }" name="Name" rules="required|min:5|max:12">
										<v-text-field color="red" v-model="name" :counter="12" :error-messages="errors" label="Name" hint="Enter your name" required></v-text-field>
									</ValidationProvider>

									<ValidationProvider v-slot="{ errors }" name="Password" rules="required|min:8">
										<v-text-field color="red" v-model="password" :error-messages="errors" :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'" :type="showPassword ? 'text' : 'password'" label="Password" hint="Enter your password" @click:append="showPassword = !showPassword"></v-text-field>
									</ValidationProvider>

									<!--<v-checkbox
                                            color="red"
                                            v-model="checkbox"
                                            label="Remember me"
                                            required
                                            @change="$v.checkbox.$touch()"
                                            @blur="$v.checkbox.$touch()"
                                    ></v-checkbox>-->
								</form>
							</ValidationObserver>
						</v-container>

						<div class="text-center">
							<v-btn color="red" text @click="signIn">SIGN IN</v-btn>
							<p class="text-center mt-3">OR</p>
							<v-btn color="red" text @click="signInToSignUpDialog">SIGN UP</v-btn>
						</div>
					</v-card-text>
				</v-card>
			</v-dialog>

			<v-dialog v-model="signUpDialog" max-width="600px">
				<v-card>
					<v-card-title>
						<span class="headline">Sign Up</span>
					</v-card-title>
					<v-card-text>
						<v-container>
							<p v-if="isSignUpError" class="text-center subtitle-2" style="color: red;">
								{{ signUpError }}
							</p>

							<ValidationObserver ref="signUpObserver">
								<form class="login">
									<ValidationProvider v-slot="{ errors }" name="Name" rules="required|max:12">
										<v-text-field color="red" v-model="name" :counter="12" :error-messages="errors" label="Name" hint="Enter your name" required></v-text-field>
									</ValidationProvider>

									<ValidationProvider v-slot="{ errors }" name="E-Mail" rules="required|email">
										<v-text-field color="red" v-model="email" :error-messages="errors" label="E-Mail" hint="Enter your E-Mail" required></v-text-field>
									</ValidationProvider>

									<ValidationProvider vid="password" v-slot="{ errors }" name="Password" rules="required|min:8">
										<v-text-field color="red" v-model="password" :error-messages="errors" :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'" :type="showPassword ? 'text' : 'password'" label="Password" hint="Enter your password" @click:append="showPassword = !showPassword"></v-text-field>
									</ValidationProvider>

									<ValidationProvider v-slot="{ errors }" name="Password repeat" rules="required|confirmed:password">
										<v-text-field color="red" v-model="passwordRepeat" :error-messages="errors" :append-icon="showRepeatPassword ? 'mdi-eye' : 'mdi-eye-off'" :type="showRepeatPassword ? 'text' : 'password'" label="Password Repeat" hint="Enter your password again" @click:append="showRepeatPassword = !showRepeatPassword"></v-text-field>
									</ValidationProvider>
									<br />
									<ValidationProvider v-slot="{ errors }" name="MoySklad Login" rules="required|max:32">
										<v-text-field color="red" v-model="MoySkladLogin" :counter="32" :error-messages="errors" label="MoySklad Login" hint="Enter your name" required></v-text-field>
									</ValidationProvider>
									<ValidationProvider vid="MoySkladPassword" v-slot="{ errors }" name="Your Sklad passowrd" rules="required|min:8">
										<v-text-field color="red" v-model="MoySkladPassword" :error-messages="errors" :append-icon="showMoySkladPassword ? 'mdi-eye' : 'mdi-eye-off'" :type="showMoySkladPassword ? 'text' : 'password'" label="MoySklad Password" hint="Enter your password" @click:append="showMoySkladPassword = !showMoySkladPassword"></v-text-field>
									</ValidationProvider>
								</form>
							</ValidationObserver>
						</v-container>
						<div class="text-center">
							<v-btn color="red" text @click="signUp">SIGN UP</v-btn>
							<p class="text-center mt-3">OR</p>
							<v-btn color="red" text @click="signUpToSignInDialog">BACK TO SIGNING IN</v-btn>
						</div>
					</v-card-text>
				</v-card>
			</v-dialog>

			<v-container fluid class="mt-n3">
				<router-view></router-view>
			</v-container>
		</v-content>

		<v-snackbar v-model="logInSnackbar" timeout="3000">
			{{ logInSnackbarText + currentName + "!" }}
			<v-btn color="pink" text @click="logInSnackbar = false">
				Close
			</v-btn>
		</v-snackbar>

		<v-snackbar v-model="logUpSnackbar" timeout="3000">
			{{ logUpSnackbarText + currentName + "!" }}
			<v-btn color="pink" text @click="logUpSnackbar = false">
				Close
			</v-btn>
		</v-snackbar>

		<v-snackbar v-model="logOutSnackbar" timeout="3000">
			{{ logOutSnackbarText }}
			<v-btn color="pink" text @click="logOutSnackbar = false">
				Close
			</v-btn>
		</v-snackbar>

		<v-snackbar v-model="logNotWorkingYetSnackbar" timeout="3000">
			Not Working ~.~
			<v-btn color="pink" text @click="logNotWorkingYetSnackbar = false">
				Close
			</v-btn>
		</v-snackbar>

		<!--<v-footer hide>
            <span>&copy; ME IRL&trade; </span>
        </v-footer>-->
	</v-app>
</template>

<script>
	import axios from "axios";
	import { AUTH_LOGOUT, AUTH_SIGN_IN_REQUEST, AUTH_SIGN_UP_REQUEST } from "./store/modules/authentication";

	import { confirmed, email, max, min, required } from "vee-validate/dist/rules";
	import { extend, setInteractionMode, ValidationObserver, ValidationProvider } from "vee-validate";

	setInteractionMode("eager");

	extend("required", {
		...required,
		message: "{_field_} can not be empty",
	});

	extend("min", {
		...min,
		message: "{_field_} must be greater than {length} characters",
	});

	extend("max", {
		...max,
		message: "{_field_} may not be greater than {length} characters",
	});

	extend("email", {
		...email,
		message: "{_field_} must be valid",
	});

	extend("confirmed", {
		...confirmed,
		message: "{_field_} is invalid",
	});

	export default {
		components: {
			ValidationProvider,
			ValidationObserver,
		},
		props: {
			source: String,
		},
		data: () => ({
			name: "",
			MoySkladLogin: "",
			email: "",
			password: "",
			MoySkladPassword: "",
			passwordRepeat: "",
			signInError: "",
			signUpError: "",
			isSignInError: false,
			isSignUpError: false,
			format_success: false, // +100500
			showPassword: false,
			showMoySkladPassword: false,
			showRepeatPassword: false,
			signInDialog: false,
			signUpDialog: false,
			drawerExpanded: true,
			userMenuExpanded: false,
			logInSnackbar: false,
			logUpSnackbar: false,
			logOutSnackbar: false,
			logNotWorkingYetSnackbar: false,
			notificationsListExpanded: true,
			logInSnackbarText: "Welcome back, ",
			logUpSnackbarText: "Welcome, ",
			logOutSnackbarText: "You have logged out.",
			userMenuItems: [
				{
					title: "Profile",
					link: "/profile",
				},
				{
					title: "Settings",
					link: "/settings",
				},
			],
			notificationItems: [
				{
					title: "Notification 1",
					link: "/notifications/1",
				},
				{
					title: "Notification 2",
					link: "/notifications/2",
				},
			],
		}),
		watch: {
			signInDialog(val) {
				this.isSignInError = false;

				if (!val) {
					this.$refs.signInObserver.reset();
					this.showPassword = false;
				}
			},

			signUpDialog(val) {
				this.isSignUpError = false;

				if (!val) {
					this.$refs.signUpObserver.reset();

					this.email = "";
					this.passwordRepeat = "";
					this.showRepeatPassword = false;
				}
			},

			isError(val) {
				if (!val) this.signInError = "";
			},
		},
		created() {
			this.$vuetify.theme.dark = true;

			axios.interceptors.response.use(undefined, function(err) {
				// eslint-disable-next-line no-unused-vars
				return new Promise(function(resolve, reject) {
					if (err.status === 401 && err.config && !err.config.__isRetryRequest) {
						// if you ever get an unauthorized, logout the user
						this.$store.dispatch(AUTH_LOGOUT);
						// you can also redirect to /login if needed !
					}
					throw err;
				});
			});
		},
		methods: {
			formatDB() {
				axios
					.delete("user/integrate", {
						Authorization: localStorage.getItem("token") || "",
					})
					.then(() => {
						this.format_success = true;
					})
					.catch(() => {
						alert("Ohh ohh some thing went wrong\n please contact your administrator");
					});
			},

			signInToSignUpDialog: function() {
				this.signInDialog = false;
				this.signUpDialog = true;
			},

			signUpToSignInDialog: function() {
				this.signUpDialog = false;
				this.signInDialog = true;
			},

			signIn: async function() {
				const isValid = await this.$refs.signInObserver.validate();

				if (isValid) {
					this.isSignInError = false;

					const { name, password } = this;

					this.$store.dispatch(AUTH_SIGN_IN_REQUEST, { name, password }).then((success) => {
						if (success) {
							this.$router.push("/dashboard");

							this.name = "";
							this.password = "";
							this.passwordRepeat = "";
							this.signInDialog = false;
							this.logInSnackbar = true;
						} else {
							this.signInError = "Invalid name or password";
							this.isSignInError = true;
						}
					});
				}
			},

			signUp: async function() {
				const isValid = await this.$refs.signUpObserver.validate();

				const { name, email, password, passwordRepeat } = this;

				if (isValid) {
					this.$store
						.dispatch(AUTH_SIGN_UP_REQUEST, {
							name,
							email,
							password,
							passwordRepeat,
						})
						.then((response) => {
							let data = response.data;
							let success = data.is_success;
							let error = data.error;

							if (success) {
								this.$router.push("/dashboard");

								this.name = "";
								this.email = "";
								this.password = "";
								this.passwordRepeat = "";
								this.signUpDialog = false;
								this.logUpSnackbar = true;
							} else {
								this.signUpError = error;
								this.isSignUpError = true;
							}
						});
				}
			},

			logout: function() {
				this.$store.dispatch(AUTH_LOGOUT).then(() => {
					this.$router.push("/");
					this.userMenuExpanded = false;
					//this.logOutSnackbar = true;
				});
			},
		},
		computed: {
			notificationBadgeNum: function() {
				return this.notificationItems.length;
			},
			currentRouteName: function() {
				return this.$route.name;
			},
			isAuthenticated: function() {
				return this.$store.getters.isAuthenticated;
			},
			currentName: function() {
				return this.$store.getters.name;
			},
		},
	};
</script>

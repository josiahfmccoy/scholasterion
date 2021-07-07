
document.addEventListener("DOMContentLoaded", (e) => {
    // Initialize Profile
    Profile.getToken().then(() => Profile.refresh());
});


const Profile = ((profile) => {
    const userPage = $('#user-page');

    const loginPage = $('#login-page');
    const loginForm = $('#login-form');

    let currentUser = null;

    const profilePage = $('#profile-page');
    const showProfilePage = () => {
        profilePage.find('#user-name-display').text(currentUser.username);
        profilePage.show();
    }

    profile.isLoggedIn = () => {
        return (currentUser != null && currentUser.token)
    };

    profile.getToken = () => {
        const loading = $.Deferred();
        $.ajax({
            url: '/api/user/check-status',
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            currentUser = data.user;
            if (currentUser != null) {
                currentUser.token = data.token;
            }
            $(document).trigger('auth:change');
            loading.resolve(currentUser);
        })
        .fail((jqXHR, status, error) => {
            currentUser = null;
            $(document).trigger('auth:change');
            loading.reject(jqXHR, status, error);
        });
        return loading.promise();
    };

    const updateNav = () => {
        const nav = $('header nav');
        if (profile.isLoggedIn()) {
            nav.find('[href="/user/logout"]').closest('.nav-item').show();
            nav.find('[href="/user/login"]').closest('.nav-item').hide();
        }
        else {
            nav.find('[href="/user/logout"]').closest('.nav-item').hide();
            nav.find('[href="/user/login"]').closest('.nav-item').show();
        }
    };

    profile.refresh = () => {
        updateNav();

        const route = Router.currentRoute();

        if (route.indexOf('user') < 0) {
            userPage.addClass('d-none');
            return $.Deferred().resolve().promise()
        }

        if (route.indexOf('logout') > -1) {
            profile.logout()
                .then(Router.redirect('/user/login'));
        }

        profilePage.hide();
        loginPage.hide();

        if (profile.isLoggedIn()) {
            if (route.indexOf('login') > -1) {
                Router.redirect('/user/profile');
            }
            const newRoute = Router.currentRoute();
            if (newRoute.indexOf('profile') > -1) {
                showProfilePage();
            }
        }
        else {
            Router.redirect('/user/login');
            loginPage.show();
        }

        userPage.removeClass('d-none');

        return $.Deferred().resolve().promise();
    };

    $.ajaxSetup({
        beforeSend: (jqXHR) => {
            if (profile.isLoggedIn()) {
                jqXHR.setRequestHeader('X-Access-Token', currentUser.token);
            }
        }
    });

    profile.login = (username, password) => {
        const loading = $.Deferred();

        if (!username || !password) {
            return loading.reject().promise();
        }

        Loader.show('login');

        const auth = 'Basic ' + btoa(username + ':' + password);

        $.ajax({
            url: '/api/user/login',
            type: 'POST',
            contentType: false,
            processData: false,
            beforeSend: (jqXHR) => jqXHR.setRequestHeader('Authorization', auth)
        })
        .done((data, status, jqXHR) => {
            currentUser = data.user;
            currentUser.token = data.token;
            $(document).trigger('auth:change');
            loading.resolve(currentUser);
            Loader.hide('login');
        })
        .fail((jqXHR, status, error) => {
            currentUser = null;
            $(document).trigger('auth:change');
            loading.reject(jqXHR, status, error);
            Loader.hide('login');
        });

        return loading.promise();
    };

    profile.logout = () => {
        return $.ajax({
            url: '/api/user/logout',
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done(() => {
            currentUser = null;
            $(document).trigger('auth:change');
        });
    };

    loginForm.on('submit', (e) => {
        e.preventDefault();

        const username = loginForm.find('#username').val();
        const password = loginForm.find('#password').val();

        profile.login(username, password);
    });

    $(document).on('router:change', () => {
        Profile.refresh();
    });
    $(document).on('auth:change', () => {
        Profile.refresh();
    });

    return profile;
})(window.Profile || {});

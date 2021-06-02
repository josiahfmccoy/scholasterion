
document.addEventListener("DOMContentLoaded", (e) => {
    // Initialize Profile
    Profile.refresh();
});


const Profile = ((profile) => {
    const loginPage = $('#login-page');

    profile.refresh = () => {
        const route = Router.currentRoute();
        if (route.indexOf('login') > -1) {
            loginPage.removeClass('d-none').addClass('d-flex');
        }
        else {
            loginPage.addClass('d-none').removeClass('d-flex');
        }
        return $.Deferred().resolve().promise();
    }

    $(document).on('router:change', () => {
        Profile.refresh();
    });

    return profile;
})(window.Profile || {});

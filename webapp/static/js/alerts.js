
document.addEventListener("DOMContentLoaded", (e) => {
    $('.toast').each(function() {
        Alerts.popup({element: this});
    });
    $('body').on('hidden.bs.toast', '.toast', function() {
        $(this).remove();
    });
});

const Alerts = ((alerts) => {
    alerts.popup = (opts) => {
        if (opts.element) {
            (new bootstrap.Toast(opts.element)).show();
            return;
        }

        const container = $('.toast-container');

        const toast = $('<div aria-live="assertive" aria-atomic="true" />')
            .attr({
                role: 'alert'
            })
            .addClass('toast fade align-items-center border-0')
            .appendTo(container);

        const btn = $('<button type="button" aria-label="Close" />')
            .attr({
                'data-bs-dismiss': 'toast'
            })
            .addClass('btn-close me-2 m-auto');

        if (opts.type) {
            toast.addClass('bg-' + opts.type + '  text-white');
        }
        if (opts.autohide === false) {
            toast.attr('data-bs-autohide', 'false');
        }

        const body = $('<div class="toast-body" />')
            .html(opts.message || '');

        if (opts.header !== undefined) {
            const header = $('<div class="toast-header" />')
                .append($('<strong class="me-auto" />').html(opts.header))
                .appendTo(toast);
            btn.appendTo(header);
            body.appendTo(toast);
        }
        else {
            const flex = $('<div class="d-flex" />')
                .appendTo(toast);
            body.appendTo(flex);
            btn.appendTo(flex);
            if (opts.type) {
                btn.addClass('btn-close-white');
            }
        }

        (new bootstrap.Toast(toast[0])).show();
    }

    return alerts;
})(window.Alerts || {});

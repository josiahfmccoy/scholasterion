
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
    };

    alerts.popover = (element, opts) => {
        const p = new bootstrap.Popover(element, opts);
        p.show();

        const btn = $('<button type="button" aria-label="Close" />')
            .attr({
                'data-bs-dismiss': 'popover'
            })
            .addClass('btn-close btn-sm p-0 ms-2 float-end');
        $(p.tip).find('.popover-header').append(btn);
    };
    $('body').on('click', '[data-bs-dismiss="popover"]', (e) => {
        e.preventDefault();
        $(e.target).closest('.popover').popover('dispose');
    });

    alerts.tooltip = (element, opts) => {
        const t = new bootstrap.Tooltip(element, opts);
        t.show();

        const tip = $(t.tip).find('.tooltip-inner');
        tip.addClass('text-white px-4 py-2').css({
            'font-size': '2em'
        });
        if (opts.header) {
            tip.prepend('<strong class="me-2">' + opts.header + '</strong>');
        }
        
        const btn = $('<button type="button" aria-label="Close" />')
            .attr({
                'data-bs-dismiss': 'tooltip',
                'style': 'font-size: 0.8em;'
            })
            .addClass('btn-close btn-close-white p-0 ms-2');

        tip.append(btn);
    };
    $('body').on('click', '[data-bs-dismiss="tooltip"]', (e) => {
        e.preventDefault();
        $(e.target).closest('.tooltip').tooltip('dispose');
    });

    return alerts;
})(window.Alerts || {});

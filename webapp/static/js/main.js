
document.addEventListener("DOMContentLoaded", (e) => {
    // Initialize I/O
    API.init();

    $('#current-text').change(function() {
        const v = $(this).val();
        if (!v) {
            return;
        }
        API.getText(v);
    });

    API.getTexts();

    $('body').on('dblclick', '.word-form', function() {
        const me = $(this);
        let form = me.text().toLowerCase().trim();
    });

    Loader.hide();
});


const API = ((api) => {
    let initialized = false;

    const body = $('body');

    api.init = () => {
        if (initialized) {
            return;
        }
        initialized = true;

        initFields();
        initForms();
    };
    const initFields = () => {
        $(window).bind('keydown', function(e) {
            if (!$('#text-content:focus').length) {
                return true;
            }
            if (e.ctrlKey || e.metaKey) {
                switch (String.fromCharCode(e.which).toLowerCase()) {
                case 's':
                    e.preventDefault();
                    $('#text-content').closest('form').submit();
                    return false;
                default:
                    break;
                }
            }
            return true
        });
        body.on('click', 'td, th', function(e) {
            const me = $(this);
            const check = me.find('input[type="checkbox"], input[type="radio"]');
            if (!check.length) {
                return;
            }
            check.prop('checked', !check.prop('checked'));
        });
    }
    const initForms = () => {
        body.on('submit', 'form', function(e) {
            e.preventDefault();
            const form = $(this);
            const msg = form.attr('data-submit-message') || 'Submitting';
            API.submit({form: form, message: msg});
        });
    }

    api.getTexts = () => {
        Loader.show('texts');
        $.ajax({
            url: 'api/texts',
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            const t = data.texts;

            const texts = $('#current-text').empty();
            texts.append('<option value="">&lt;Select a Document&gt;</option>');
            for (const txt of t) {
                texts.append('<option value="' + txt.value + '">' + txt.label + '</option>');
            }
            texts.val(t[0].value).change();
            Loader.hide('texts');
        })
        .fail((jqXHR, status, error) => {
            Loader.hide('texts');
        });
    };

    api.getText = (name) => {
        Loader.show('text');
        $.ajax({
            url: 'api/text?name=' + name,
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            $('#reading-page').html(data.content || '');
            Loader.hide('text');
        })
        .fail((jqXHR, status, error) => {
            $('#reading-page').html('Unable to load ' + name);
            Loader.hide('text');
        });
    };

    api.submit = (opts) => {
        if (opts.link) {
            const form = $('<form method="GET" />')
                .attr({action: opts.link.attr('href')});
            opts.form = form;
            opts.btn = opts.link;
        }
        const submission = $.Deferred();

        let btn = opts.btn;
        if (opts.btn === undefined && opts.form) {
            btn = opts.form.find('button[type="submit"]');
        }
        let origMsg = '';
        if (btn && btn.length) {
            const msg = opts.message || 'Loading';
            origMsg = btn[0].innerHTML;
            btn.html(
                '<span class="spinner-border spinner-border-sm"' +
                ' role="status" aria-hidden="true"></span>' +
                '&nbsp;<span>' + msg + ' ...</span>'
            ).prop('disabled', true);
            if (btn.is('a')) {
                btn.css('pointer-events', 'none');
                btn.addClass('disabled');
            }
        }

        submission.always(() => {
            if (btn && btn.length) {
                btn.html(origMsg).prop('disabled', false);
                if (btn.is('a')) {
                    btn.css('pointer-events', '');
                    btn.removeClass('disabled');
                }
            }
        });

        if (opts.form) {
            submitForm(opts)
                .done((data, status, jqXHR) => {
                    if (data.job_id === undefined) {
                        submission.resolve(data, status, jqXHR);
                        return;
                    }

                    setTimeout(() => {
                        checkJob(data.job_id).done((data) => {
                            submission.resolve(data);
                        })
                    }, 1000);
                })
                .fail((jqXHR, status, error) => {
                    Alerts.popup({
                        header: error,
                        message: jqXHR.responseJSON.message,
                        type: 'danger',
                        autohide: false
                    });
                    submission.reject(jqXHR, status, error);
                });
        }
        else {
            submission.resolve();
        }

        return submission.promise();
    };

    const submitForm = (opts) => {
        const form = opts.form;

        // Disable dataTables paging
        form.find('table.dataTable').each((i, tbl) => {
            const me = $(tbl);
            const dt = me.DataTable();
            const pg = dt.page();
            const len = dt.page.len();

            me.attr('data-page', pg);
            me.attr('data-page-len', len);

            dt.page.len(-1).draw();
        });

        const formData = new FormData(form[0]);

        // Re-enable dataTables paging
        form.find('table.dataTable').each((i, tbl) => {
            const me = $(tbl);
            const dt = me.DataTable();
            const pg = parseInt(me.attr('data-page') || 0);
            const len = parseInt(me.attr('data-page-len') || 10);
            dt.page.len(len).draw();
            dt.page(pg).draw('page');

            me.removeAttr('data-page');
            me.removeAttr('data-page-len');
        });

        form.find('input[type="date"], input[type="datetime-local"]').each(function() {
            // Convert dates to UTC
            const input = $(this);
            const name = input.attr('name');
            formData.delete(name);

            const d = moment(input.val()).utc();
            formData.set(name, d.format('YYYY-MM-DDTHH:mm'));
        })

        const errs = form.find('.invalid-feedback');
        errs.remove();

        const url = form.attr('action');
        const method = form.attr('method') || 'POST';

        const submission = $.Deferred();

        $.ajax({
            url: url,
            type: method,
            data: formData,
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            try {
                submission.resolve(data, status, jqXHR);
            }
            finally {
            }
        })
        .fail((jqXHR, status, error) => {
            try {
                submission.reject(jqXHR, status, error);
            }
            finally {
            }
        });

        return submission.promise();
    };

    const checkJob = (jobId) => {
        const check = $.Deferred();

        $.ajax({
            url: '/api/job/' + jobId,
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data) => {
            if (data.status === 'complete') {
                if (data.error !== undefined) {
                    check.reject({
                        responseJSON: {message: data.error}
                    },
                    'error',
                    'JOB FAILED');
                }
                check.resolve(data);
            }
            else {
                setTimeout(() => {
                    checkJob(jobId).done((data) => {
                        check.resolve(data);
                    })
                }, 500);
            }
        });

        return check.promise();
    };

    return api;
})(window.API || {});


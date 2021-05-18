
document.addEventListener("DOMContentLoaded", (e) => {
    // Initialize I/O
    API.init();

    // Initialize Reader
    Reader.refresh();

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


const Router = ((router) => {
    router.currentRoute = () => {
        const path = window.location.pathname;
        return path.split('/').filter(x => x.trim() != '');
    };

    router.goTo = (path, html, pageTitle) => {
        const s = {};
        if (html) {
            s.html = html;
        }
        if (pageTitle) {
            s.pageTitle = pageTitle;
        }
        window.history.pushState(
            s, '', window.location.origin + '/' + path
        );
        Reader.refresh();
    };

    $(() => {
        $(window).on('popstate', () => {
            if (window.location.hash) {
                return;
            }
            Reader.refresh();
        });
    });

    return router;
})(window.Router || {});


const Reader = ((reader) => {
    const currentTextSelect = $('#current-text');
    const currentVolSelect = $('#current-volume');
    const readingPage = $('#reading-page');

    let currentText = {};
    let currentVolume = {};

    reader.refresh = () => {
        loadTexts().done((texts) => reader.setTextOpts(texts));
    }

    const loadTexts = () => {
        Loader.show('texts');
        const loading = $.Deferred();

        $.ajax({
            url: '/api/text',
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            loading.resolve(data.texts);
            Loader.hide('texts');
        })
        .fail((jqXHR, status, error) => {
            loading.reject(jqXHR, status, error);
            Loader.hide('texts');
        });

        return loading.promise();
    };
    reader.setTextOpts = (texts) => {
        const route = Router.currentRoute();
        const currentVal = route[0] || '';

        currentTextSelect.empty()
            .append('<option value="">&lt;Select a Document&gt;</option>');
        for (const txt of texts) {
            const o = $('<option />')
                .attr({
                    'value': txt.id
                })
                .text(txt.name + ' (' + txt.language.name + ')')
                .appendTo(currentTextSelect);
            if (txt.id == currentVal) {
                o.attr('selected', 'selected');
            }
        }
        currentTextSelect.val(currentVal);
        if (currentVal) {
            loadText(currentVal);
        }
    };

    const loadText = (id) => {
        Loader.show('text');
        const loading = $.Deferred();

        $.ajax({
            url: '/api/text/' + parseInt(id),
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            reader.setText(data.text);
            Loader.hide('text');
        })
        .fail((jqXHR, status, error) => {
            loading.reject(jqXHR, status, error);
            Loader.hide('text');
        });

        return loading.promise();
    };
    reader.setText = (text) => {
        currentText = text;

        const route = Router.currentRoute();
        const currentVol = route[1] || '';

        currentVolSelect.empty()
            .closest('div').toggle(text.volumes.length > 1);
        for (const vol of text.volumes) {
            const o = $('<option />')
                .attr({
                    'value': vol.id,
                    'data-url': vol.file_url
                })
                .text(vol.name)
                .appendTo(currentVolSelect);
            if (vol.id == currentVol) {
                o.attr('selected', 'selected');
            }
        }
        if (!currentVol && text.volumes.length) {
            loadVolume(text.volumes[0].id);
        }
        else if (currentVol) {
            loadVolume(currentVol);
        }
    };

    const loadVolume = (id) => {
        Loader.show('volume');
        const loading = $.Deferred();

        $.ajax({
            url: '/api/volume/' + parseInt(id),
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            reader.setVolume(data.volume);
            Loader.hide('volume');
        })
        .fail((jqXHR, status, error) => {
            loading.reject(jqXHR, status, error);
            Loader.hide('volume');
        });

        return loading.promise();
    };
    reader.setVolume = (vol) => {
        currentVolume = vol;

        loadContent(vol.file_url).done((xml) => reader.setContent(xml));
    };

    const loadContent = (url) => {
        if (url.indexOf('http') != 0) {
            if (url.indexOf('/static/data') != 0) {
                url = '/static/data/' + url;
            }
        }
        Loader.show('content');
        const loading = $.Deferred();

        $.ajax({
            url: url,
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            loading.resolve(data.documentElement || {});
            Loader.hide('content');
        })
        .fail((jqXHR, status, error) => {
            loading.reject(jqXHR, status, error);
            Loader.hide('content');
        });

        return loading.promise();
    };
    reader.setContent = (xml) => {
        readingPage.html(xml.outerHTML || '');
    };

    currentTextSelect.change((e) => {
        const v = e.target.value;
        if (!v || v == currentText.id) {
            return;
        }
        Router.goTo(v);
    });
    currentVolSelect.change((e) => {
        const v = e.target.value;
        if (!v || v == currentVolume.id) {
            return;
        }
        Router.goTo(currentText.id + '/' + v);
    });

    $('body').on('dblclick', '.word-form', function() {
        const me = $(this);
        let form = me.text().toLowerCase().trim();

        const lemma = me.siblings('.lemma');
        if (!lemma.length) {
            return;
        }
        const lem = [];
        for (const el of lemma) {
            lem.push(el.innerText);
        }

        const gls = [];
        const contextGloss = me.siblings('.gloss');
        if (contextGloss.length) {
            gls.push(contextGloss.text());
        }
        else {
            // TODO; use glossing API
        }

        Alerts.popup({
            header: lem.join('; '),
            message: '<ul><li>' + gls.join('</li><li>') + '</li></ul>',
            type: 'light',
            // autohide: false
        });
    });

    return reader;
})(window.Reader || {});
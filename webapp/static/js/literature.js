
document.addEventListener("DOMContentLoaded", (e) => {
    // Initialize Reader
    Reader.refresh().done(() => { Loader.hide(); });
});


const Reader = ((reader) => {
    const litViewer = $('#literature-viewer');
    const currentTextSelect = $('#current-text');
    const currentVolSelect = $('#current-volume');
    const readingPage = $('#reading-page');

    let currentText = {};
    let currentVolume = {};

    reader.refresh = () => {
        if (Router.currentRoute().indexOf('library') < 0) {
            litViewer.addClass('d-none').removeClass('d-flex');
            return $.Deferred().resolve([]).promise();
        }
        else {
            litViewer.removeClass('d-none').addClass('d-flex');
            return loadTexts().done((texts) => reader.setTextOpts(texts));
        }
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
        const currentVal = route[1] || '';

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
        return loadText(currentTextSelect.val() || {}).done((text) => reader.setText(text));
    };

    const loadText = (id) => {
        const loading = $.Deferred();
        if (currentText.id == id) {
            return loading.resolve(currentText).promise();
        }

        Loader.show('text');

        $.ajax({
            url: '/api/text/' + parseInt(id),
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            loading.resolve(data.text);
            Loader.hide('text');
        })
        .fail((jqXHR, status, error) => {
            loading.reject(jqXHR, status, error);
            Loader.hide('text');
        });

        return loading.promise();
    };
    reader.setText = (text) => {
        currentText = text || {};
        currentText.volumes = currentText.volumes || [];

        const route = Router.currentRoute();
        const currentVol = route[2] || ((currentText.volumes[0] || {}).id || '');

        currentVolSelect.empty()
            .closest('div').toggle(currentText.volumes.length > 1);
        for (const vol of currentText.volumes) {
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
        loadVolume(currentVol).done((vol) => reader.setVolume(vol));
    };

    const loadVolume = (id) => {
        const loading = $.Deferred();
        if (currentVolume.id == id) {
            return loading.resolve(currentVolume).promise();
        }

        Loader.show('volume');

        $.ajax({
            url: '/api/volume/' + parseInt(id),
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            loading.resolve(data.volume);
            Loader.hide('volume');
        })
        .fail((jqXHR, status, error) => {
            loading.reject(jqXHR, status, error);
            Loader.hide('volume');
        });

        return loading.promise();
    };
    reader.setVolume = (vol) => {
        currentVolume = vol || {};
        return loadContent(currentVolume.file_url)
            .done((xml) => reader.setContent(xml));
    };

    const loadContent = (url) => {
        const loading = $.Deferred();
        if (!url) {
            return loading.resolve({}).promise();
        }

        if (url.indexOf('http') != 0) {
            if (url.indexOf('/static/data') != 0) {
                url = '/static/data/' + url;
            }
        }
        Loader.show('content');

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
        readingPage.empty();
        if ($.isEmptyObject(xml)) {
            return;
        }
        $('<div class="lang-' + (currentText.language || {}).iso_code + '" />')
            .html(xml.outerHTML || '')
            .appendTo(readingPage);
    };

    currentTextSelect.change((e) => {
        const v = e.target.value;
        if (!v || v == currentText.id) {
            return;
        }
        Router.goTo('library/' + v);
    });
    currentVolSelect.change((e) => {
        const v = e.target.value;
        if (!v || v == currentVolume.id) {
            return;
        }
        Router.goTo('library/' + currentText.id + '/' + v);
    });

    const loadParsing = (vol_id, token_id) => {
        // Loader.show('parsing');
        const loading = $.Deferred();

        $.ajax({
            url: '/api/volume/' + parseInt(vol_id) + '/token/' + token_id,
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            loading.resolve(data.token);
            Loader.hide('parsing');
        })
        .fail((jqXHR, status, error) => {
            loading.reject(jqXHR, status, error);
            // Loader.hide('parsing');
        });

        return loading.promise();
    };

    const showToken = (element, token) => {
        if (!token) {
            return;
        }
        const lem = token.words.map(x => x.lexeme.lemma);
        const gls = [];
        if (token.gloss) {
            gls.push(token.gloss);
        }
        else {
            for (const g of token.words.map(x => x.lexeme.gloss)) {
                if (g) {
                    gls.push(g);
                }
            }
        }
        Alerts.popover(element, {
            title: lem.join('; '),
            content: gls.join('</ br>'),
            html: true,
            placement: 'left'
        });

        // Alerts.tooltip(element, {
        //     header: lem.join('; '),
        //     title: gls.join('; ') || '...',
        //     html: true,
        //     trigger: 'manual'
        // });

        // Alerts.popup({
        //     header: lem.join('; '),
        //     message: '<ul><li>' + gls.join('</li><li>') + '</li></ul>',
        //     type: 'light',
        //     // autohide: false
        // });
    };

    $('body').on('keyup', (e) => {
        if (e.key === 'Escape') {
            $('.popover').popover('dispose');
        }
    });
    $('body').on('dblclick', '.word', (e) => {
        e.preventDefault();

        const me = $(e.target);

        const t = me.attr('data-token');
        if (t) {
            showToken(e.target, JSON.parse(t));
        }
        else {
            const id = me.attr('id');

            loadParsing(currentVolume.id, id)
                .done((token) => {
                    if (token == null) {
                        return;
                    }
                    me.attr('data-token', JSON.stringify(token));
                    showToken(e.target, token);
                });
        }
    });

    $(document).on('router:change', () => {
        Reader.refresh();
    });

    return reader;
})(window.Reader || {});

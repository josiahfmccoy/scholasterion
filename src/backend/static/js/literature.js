
document.addEventListener("DOMContentLoaded", (e) => {
    // Initialize Reader
    Reader.refresh().done(() => { Loader.hide(); });
});


const Reader = ((reader) => {
    const libraryPage = $('#library-page');

    const frontDeskPage = $('#front-desk-page');
    const readingPage = $('#reading-page');

    reader.refresh = () => {
        const route = Router.currentRoute();

        const loading = $.Deferred();

        if (route.indexOf('library') < 0) {
            libraryPage.addClass('d-none');
            return loading.resolve().promise();
        }

        readingPage.hide();
        frontDeskPage.hide();

        if (route.indexOf('reader') < 0) {
            loadCollections().done((cols) => {
                reader.showCollections(cols);
                frontDeskPage.show();
                loading.resolve();
            });
        }
        else {
            reader.load().done(() => loading.resolve());
        }

        loading.done(() => libraryPage.removeClass('d-none'));

        return loading.promise();
    }

    const loadCollections = () => {
        Loader.show('collections');
        const loading = $.Deferred();

        $.ajax({
            url: '/api/collection',
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            loading.resolve(data.collections);
            Loader.hide('collections');
        })
        .fail((jqXHR, status, error) => {
            loading.reject(jqXHR, status, error);
            Loader.hide('collections');
        });

        return loading.promise();
    };
    reader.showCollections = (collections) => {
        const root = frontDeskPage.find('.card-body').empty();

        const langSectionMap = {}

        for (const col of collections) {
            if (langSectionMap[col.language.id] === undefined) {
                $('<h3 class="mb-2" />')
                    .text(col.language.name + ' (' + col.language.iso_code + ')')
                    .appendTo(root);
                langSectionMap[col.language.id] = $('<ul class="mb-3" />')
                    .appendTo(root);
            }

            const container = langSectionMap[col.language.id];
            const li = $('<li class="mb-1" />')
                .appendTo(container);

            let title = col.title.replace(/\\n/g, ' ');
            if (col.author) {
                title += ' (' + col.author + ')'
            }
            $('<a />')
                .attr('href', '/library/reader/' + col.id)
                .text(title)
                .appendTo(li);
        }
    };

    let currentCollection = {};
    let currentDocument = {}

    reader.load = () => {
        const route = Router.currentRoute();

        const loading = $.Deferred();

        const i = route.indexOf('reader') + 1;
        loadCollection(route[i])
            .done((col) => {
                reader.setCollection(col);
                readingPage.show();
                loading.resolve(col);
            })
            .fail((jqXHR, status, error) => {
                loading.reject(jqXHR, status, error);
            });

        return loading.promise();
    };

    const processCollection = (col) => {
        col = col || {};
        col.documents = col.documents || [];
        col.sections = col.sections || [];
        col.children = col.documents.concat(col.sections)
            .sort((a, b) => a.order - b.order);

        col.htmlTitle = () => {
            return (col.long_title || col.title)
                .replace(/\\n/g, ' ')
                .replace(/\n/g, ' ');
        };

        return col;
    };

    const loadCollection = (id) => {
        const loading = $.Deferred();
        if (currentCollection.id == id) {
            return loading.resolve(currentCollection).promise();
        }

        Loader.show('collection');

        $.ajax({
            url: '/api/collection/' + parseInt(id),
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            loading.resolve(data.collection);
            Loader.hide('collection');
        })
        .fail((jqXHR, status, error) => {
            loading.reject(jqXHR, status, error);
            Loader.hide('collection');
        });

        return loading.promise();
    };
    reader.setCollection = (col) => {
        currentCollection = processCollection(col);

        const route = Router.currentRoute();

        let activeElement = currentCollection;
        let hLevel = 1;
        displayHeader(activeElement, hLevel);

        const path = [];

        let i = route.indexOf('reader') + 1;
        while (i + 1 < route.length) {
            const idx = route[i + 1];
            const d = activeElement.children[idx - 1];
            if (d === undefined) {
                break;
            }
            path.push(idx);
            activeElement = processCollection(d);
            i++;
            if (activeElement.file_url !== undefined) {
                break;
            }
            hLevel++;
            displayHeader(activeElement, hLevel);
        }

        if (activeElement.file_url !== undefined) {
            return reader.setDocument(activeElement);
        }
        else {
            displayToC(activeElement, path);
            return $.Deferred().resolve().promise();
        }
    };

    const displayHeader = (col, lvl) => {
        const header = readingPage.find('#page-header');
        const e = header.find('h' + lvl);
        if (e.length) {
            e.remove();
        }

        const h = $('<h' + lvl + ' />')
            .html(col.long_title.replace(/\\n/g, '<br/>'))
            .appendTo(header);

        if (lvl == 1) {
            h.addClass('text-center');
            h.prependTo(header);
        }
    };

    const displayToC = (col, path) => {
        const page = readingPage.find('#page-body').empty();

        const drawToC = (parent, vol, subPath, listStyle) => {
            const ul = $('<ul />')
                .appendTo(parent);
            if (listStyle !== undefined) {
                ul.css('list-style-type', listStyle);
            }

            for (let i = 0; i < vol.children.length; i++) {
                const c = processCollection(vol.children[i]);
                const li = $('<li class="mb-1" />').appendTo(ul);
                $('<a />').text(c.htmlTitle())
                    .attr({
                        href: (
                            '/library/reader/' + currentCollection.id
                            + '/' + subPath + '/' + (i + 1)
                        ).replace(/\/\//g, '/')
                    })
                    .appendTo(li);

                if (c.children && c.children.length) {
                    drawToC(li, c, subPath + '/' + (i + 1));
                }
            }
        };

        drawToC(page, col, path.join('/'), '"\\00A7\\0020"');
    }

    reader.setDocument = (doc) => {
        currentDocument = doc || {};
        return loadContent(currentDocument.file_url)
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
        const page = readingPage.find('#page-body').empty();

        if ($.isEmptyObject(xml)) {
            return;
        }
        $('<div class="lang-' + (currentCollection.language || {}).iso_code + '" />')
            .html(xml.outerHTML || '')
            .appendTo(page);
    };

    const loadParsing = (vol_id, token_id) => {
        // Loader.show('parsing');
        const loading = $.Deferred();

        $.ajax({
            url: '/api/document/' + parseInt(vol_id) + '/token/' + token_id,
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

            loadParsing(currentDocument.id, id)
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

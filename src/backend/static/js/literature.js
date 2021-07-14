
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
            loadDocuments().done((docs) => {
                reader.showDocuments(docs);
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

    const loadDocuments = () => {
        Loader.show('documents');
        const loading = $.Deferred();

        $.ajax({
            url: '/api/document',
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            loading.resolve(data.documents);
            Loader.hide('documents');
        })
        .fail((jqXHR, status, error) => {
            loading.reject(jqXHR, status, error);
            Loader.hide('documents');
        });

        return loading.promise();
    };
    reader.showDocuments = (documents) => {
        const root = frontDeskPage.find('.card-body').empty();

        const langSectionMap = {};
        const authorMap = {};

        for (const doc of documents) {
            if (langSectionMap[doc.language.id] === undefined) {
                $('<h3 class="mb-2" />')
                    .text(doc.language.name + ' (' + doc.language.iso_code + ')')
                    .appendTo(root);
                langSectionMap[doc.language.id] = $('<div class="mb-3" />')
                    .appendTo(root);
            }

            const container = langSectionMap[doc.language.id];

            const authorKey = (doc.author || 'Anonymous') + '-' + doc.language.id;
            if (authorMap[authorKey] === undefined) {
                $('<h4 class="ms-2 mb-2" />')
                    .text(doc.author || 'Anonymous')
                    .appendTo(container);
                authorMap[authorKey] = $('<ul class="ms-2 mb-2" />')
                    .appendTo(container);
            }

            const subcontainer = authorMap[authorKey];
            const li = $('<li class="mb-1" />')
                .appendTo(subcontainer);

            let title = doc.title.replace(/\\n/g, ' ');
            $('<a />')
                .attr('href', '/library/reader/' + doc.id)
                .text(title)
                .appendTo(li);
        }
    };

    let currentDocument = {}

    reader.load = () => {
        const route = Router.currentRoute();

        const loading = $.Deferred();

        const i = route.indexOf('reader') + 1;
        loadDocument(route[i])
            .done((doc) => {
                reader.setDocument(doc);
                readingPage.show();
                loading.resolve(doc);
            })
            .fail((jqXHR, status, error) => {
                loading.reject(jqXHR, status, error);
            });

        return loading.promise();
    };

    const loadDocument = (id) => {
        const loading = $.Deferred();
        if (currentDocument.id == id) {
            return loading.resolve(currentDocument).promise();
        }

        Loader.show('document');

        $.ajax({
            url: '/api/document/' + parseInt(id),
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            loading.resolve(data.document);
            Loader.hide('document');
        })
        .fail((jqXHR, status, error) => {
            loading.reject(jqXHR, status, error);
            Loader.hide('document');
        });

        return loading.promise();
    };
    reader.setDocument = (doc) => {
        currentDocument = doc;

        return loadContent(currentDocument.id)
            .done((content) => reader.setContent(content));
    };

    const loadContent = (docId, filename) => {
        const loading = $.Deferred();

        Loader.show('content');

        const url = ['/api/document/' + parseInt(docId) + '/content'];
        const args = [];
        if (filename !== undefined) {
            args.push('filename=' + encodeURIComponent(filename));
        }
        url.push(args.join('&') || '');
        

        $.ajax({
            url: url.join('?'),
            type: 'GET',
            contentType: false,
            processData: false
        })
        .done((data, status, jqXHR) => {
            loading.resolve(data.content || {});
            Loader.hide('content');
        })
        .fail((jqXHR, status, error) => {
            loading.reject(jqXHR, status, error);
            Loader.hide('content');
        });

        return loading.promise();
    };
    reader.setContent = (content) => {
        const route = Router.currentRoute();

        const page = readingPage.find('#page-body').empty();

        if ($.isEmptyObject(content)) {
            return;
        }

        const searchParams = (new URL(window.location.href)).searchParams;
        const sect = (searchParams.get('section') || '').split('/');

        const findSection = (section, identifier) => {
            if (!(identifier || '').trim()) {
                return section;
            }
            for (let i = 0; i < section.sections.length; i++) {
                const s = section.sections[i];
                let check = s.title_page || s.table_of_contents || s.text;
                if (check.indexOf('./') === 0) {
                    check = check.slice(2);
                }
                if (check.indexOf(identifier) === 0) {
                    return s
                }
            }
            return null;
        }

        let currentSection = content;

        for (let i = 0; i < sect.length; i++) {
            if (currentSection.title_page !== undefined) {
                const titlePage = $('<div />').appendTo(page);
                loadContent(currentDocument.id, currentSection.title_page)
                    .done((xml) => titlePage[0].outerHTML = xml);
            }
            currentSection = findSection(currentSection, sect.slice(0, i + 1).join('/'));
            if (currentSection === null) {
                return;
            }
        }
        if (currentSection !== content && currentSection.title_page !== undefined) {
            const titlePage = $('<div />').appendTo(page);
            loadContent(currentDocument.id, currentSection.title_page)
                .done((xml) => titlePage[0].outerHTML = xml);
        }

        if (currentSection.table_of_contents !== undefined) {
            const toc = $('<div />').appendTo(page);
            loadContent(currentDocument.id, currentSection.table_of_contents)
                .done((xml) => toc[0].outerHTML = xml);
        }
        if (currentSection.text !== undefined) {
            const txt = $('<div />').appendTo(page);
            loadContent(currentDocument.id, currentSection.text)
                .done((xml) => txt[0].outerHTML = xml);
        }
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

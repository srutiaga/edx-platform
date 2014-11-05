define(['jquery', 'js/edxnotes/notes', 'jasmine-jquery'],
    function($, Notes) {
        'use strict';

        describe('Test Shim', function() {
            var annotators = [], highlights = [];

            // We currently run JQuery 1.7.2 in Jasmine tests and LMS.
            // AnnotatorJS 1.2.9. uses two calls to addBack (in the two
            // functions 'isAnnotator' and 'onHighlightMouseover') which was
            // only defined in JQuery 1.8.0. In LMS, it works without throwing
            // an error because jQuery.UI 1.10.0 adds support to jQuery<1.8 by
            // augmenting $.fn with that missing function. We do the same here.
            if (!$.fn.addBack) {
                $.fn.addBack = function(selector) {
                    return this.add(selector == null ?
                            this.prevObject : this.prevObject.filter(selector)
                    );
                };
            }

            function checkAnnotatorsAreFrozen() {
                _.each(annotators, function(annotator) {
                    expect(annotator.isFrozen).toBe(true);
                    expect(annotator.onHighlightMouseover).not.toHaveBeenCalled();
                    expect(annotator.startViewerHideTimer).not.toHaveBeenCalled();
                });
            }

            function checkAnnotatorsAreUnfrozen() {
                _.each(annotators, function(annotator) {
                    expect(annotator.isFrozen).toBe(false);
                    expect(annotator.onHighlightMouseover).toHaveBeenCalled();
                    expect(annotator.startViewerHideTimer).toHaveBeenCalled();
                });
            }

            beforeEach(function() {
                loadFixtures('js/fixtures/edxnotes/edxnotes.html');
                annotators = [
                    Notes.factory($('div#edx-notes-wrapper-123').get(0), {}),
                    Notes.factory($('div#edx-notes-wrapper-456').get(0), {})
                ];
                _.each(annotators, function(annotator, index) {
                    highlights.push($('<span class="annotator-hl" />').appendTo(annotators[index].element));
                    spyOn(annotator, 'onHighlightClick').andCallThrough();
                    spyOn(annotator, 'onHighlightMouseover').andCallThrough();
                    spyOn(annotator, 'startViewerHideTimer').andCallThrough();
                });
            });

            it('Test that clicking a highlight freezes mouseover and mouseout in all highlighted text', function() {
                _.each(annotators, function(annotator) {
                    expect(annotator.isFrozen).toBe(false);
                });
                highlights[0].click();
                // Click is attached to the onHighlightClick event handler which
                // in turn calls onHighlightMouseover.
                // To test if onHighlightMouseover is called or not on
                // mouseover, we'll have to reset onHighlightMouseover.
                expect(annotators[0].onHighlightClick).toHaveBeenCalled();
                expect(annotators[0].onHighlightMouseover).toHaveBeenCalled();
                annotators[0].onHighlightMouseover.reset();

                // Check that both instances of annotator are frozen
                _.invoke(highlights, 'mouseover');
                _.invoke(highlights, 'mouseout');
                checkAnnotatorsAreFrozen();
            });

            it('Test that clicking twice reverts to default behavior', function() {
                highlights[0].click();
                $(document).click();
                annotators[0].onHighlightMouseover.reset();

                // Check that both instances of annotator are unfrozen
                _.invoke(highlights, 'mouseover');
                _.invoke(highlights, 'mouseout');
                checkAnnotatorsAreUnfrozen();
            });
        });
    }
);

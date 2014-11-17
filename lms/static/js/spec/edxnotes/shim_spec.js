define(['jquery', 'underscore', 'js/edxnotes/notes', 'jasmine-jquery'],
    function($, _, Notes) {
        'use strict';

        describe('Test Shim', function() {
            var annotators = [], highlights = [];

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
                highlights = [];
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

            it('Test that destroying an instance sets all others to unfrozen and unbinds document events', function() {
                var events;
                // Freeze all instances
                highlights[0].click();
                // Destroy first instance
                annotators[0].destroy();
                // Check that click:edxnotes:freeze is not bound to the document element
                events = $._data(document, 'events').click;
                _.each(events, function(event) {
                    expect(event.namespace).not.toBe('edxnotes:freeze');
                });

                // Check that the remaining instance is unfrozen
                highlights[1].mouseover();
                highlights[1].mouseout();
                expect(annotators[1].isFrozen).toBe(false);
                expect(annotators[1].onHighlightMouseover).toHaveBeenCalled();
                expect(annotators[1].startViewerHideTimer).toHaveBeenCalled();
            });
        });
    }
);

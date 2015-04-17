(function(define) {
'use strict';
// VideoPlayPlaceholder module.
define(
'video/09_play_placeholder.js', [],
function() {
    /**
     * Video volume control module.
     * @exports video/09_play_placeholder.js
     * @constructor
     * @param {Object} state The object containing the state of the video
     * @param {Object} i18n The object containing strings with translations.
     * @return {jquery Promise}
     */
    var PlayPlaceholder = function(state, i18n) {
        if (!(this instanceof PlayPlaceholder)) {
            return new PlayPlaceholder(state, i18n);
        }

        _.bindAll(this, 'hide', 'show', 'onClick', 'destroy');
        this.state = state;
        this.state.videoPlayPlaceholder = this;
        this.i18n = i18n;
        this.initialize();

        return $.Deferred().resolve().promise();
    };

    PlayPlaceholder.prototype = {
        destroy: function () {
            this.state.el.off('destroy', this.destroy);
            this.el.off({
                'click': this.onClick,
                'play': this.hide,
                'pause': this.show
            });
            delete this.state.videoPlayPlaceholder;
        },

        isSupportedDevice: function () {
            return /iPad|Android/i.test(this.state.isTouch[0]) && !this.state.isYoutubeType();
        },

        /** Initializes the module. */
        initialize: function() {
            if (!this.isSupportedDevice()) {
                return false;
            }

            this.el = this.state.find('.btn-play');
            this.bindHandlers();
            this.show();
        },

        /** Bind any necessary function callbacks to DOM events. */
        bindHandlers: function() {
            this.el.on({
                'click': this.onClick,
                'play': this.hide,
                'pause': this.show
            });
            this.state.el.on('destroy', this.destroy);
        },

        onClick: function (event) {
            event.preventDefault();
            this.state.videoCommands.execute('togglePlayback');
        },

        hide: function () {
            this.el
                .addClass('is-hidden')
                .attr({'aria-hidden': 'true', 'tabindex': -1});
        },

        show: function () {
            this.el
                .removeClass('is-hidden')
                .attr({'aria-hidden': 'false', 'tabindex': 0});
        }
    };

    return PlayPlaceholder;
});
}(RequireJS.define));

(function (define) {

// VideoCaption module.
define(
'video/09_bumper.js',
['video/01_initialize.js'],
function (Initialize) {
    /**
     * VideoBumper module exports a function.
     *
     * @type {function}
     * @access public
     *
     * @param {object} state - The object containing the state of the video
     *     player. All other modules, their parameters, public variables, etc.
     *     are available via this object.
     *
     * @this {object} The global window object.
     *
     * @returns {jquery Promise}
     */
    var VideoBumper = function (state, element) {
        if (!(this instanceof VideoBumper)) {
            return new VideoBumper(state, element);
        }

        this.dfd = $.Deferred();
        this.element = $(element);
        this.state = state;
        this.state.videoBumper = this;
        _.bindAll(this, 'showMainVideo');
        this.renderElements();
        this.bindHandlers();
        this.initialize();
        return this.dfd.promise();
    };

    VideoBumper.prototype = {
        initialize: function () {
            // TODO: Remove this line
            this.controls = $('.video-controls', this.state.el).clone();

            // TODO: Remove this line;
            this.state.metadata.sources = [
                'http://www.w3schools.com/html/mov_bbb.mp4'
            ];
            Initialize(this.state, this.element);
        },

        showMainVideo: function () {
            this.destroy();
            this.dfd.resolve();
        },

        canShowVideo: function () {
            return (this.dfd.isResolved() || this.dfd.isRejected());
        },

        skip: function () {
            this.element.trigger('skip');
        },

        skipAndDoNotShowAgain: function () {
            this.skip();
            // TODO: send request.
        },

        /**
         * Initiate rendering of elements, and set their initial configuration.
         */
        renderElements: function () {
            // TODO: Replace this line.
            $('.add-fullscreen, .volume, .speeds, .slider', this.state.el).css('visibility', 'hidden');
        },

        /**
         * Bind any necessary function callbacks to DOM events (click, mousemove, etc.).
         *
         */
        bindHandlers: function () {
            var events = ['ended', 'skip', 'error'].join(' ');
            this.element.on(events, this.showMainVideo);
        },

        destroy: function () {
            var player = this.state.videoPlayer.player;
            if (player && player.destroy) {
                player.destroy();
            } else {
                $('video', this.element).remove();
            }
            // TODO: Remove this line
            $('.video-controls', this.element).replaceWith(this.controls);
        }
    };

    return VideoBumper;
});

}(RequireJS.define));

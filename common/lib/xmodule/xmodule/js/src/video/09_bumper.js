(function (define) {

// VideoCaption module.
define(
'video/09_bumper.js',
[], function () {
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
    var VideoBumper = function (player, state, element) {
        if (!(this instanceof VideoBumper)) {
            return new VideoBumper(state, element);
        }

        _.bindAll(this, 'showMainVideo', 'destroy');
        this.dfd = $.Deferred();
        this.element = $(element);
        this.player = player;
        this.state = state;
        this.doNotShowAgain = false;
        this.state.videoBumper = this;
        this.renderElements();
        this.bindHandlers();
        this.initialize();
    };

    VideoBumper.prototype = {
        initialize: function () {
            this.player(this.state, this.element);
        },

        getPromise: function () {
            return this.dfd.promise();
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
            this.doNotShowAgain = true;
            this.skip();
            // TODO: send a request.
        },

        /**
         * Initiate rendering of elements, and set their initial configuration.
         */
        renderElements: function () {},

        /**
         * Bind any necessary function callbacks to DOM events (click, mousemove, etc.).
         *
         */
        bindHandlers: function () {
            var events = ['ended', 'skip', 'error'].join(' ');
            this.element.on(events, this.showMainVideo);
        },

        destroy: function () {
            var events = ['ended', 'skip', 'error'].join(' ');
            this.element.off(events, this.showMainVideo);
            if (_.isFunction(this.state.videoPlayer.destroy)) {
                this.state.videoSaveStatePlugin.onSkip(this.doNotShowAgain);
                this.state.videoPlayer.destroy();
            }
        }
    };

    return VideoBumper;
});

}(RequireJS.define));

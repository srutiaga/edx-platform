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

        _.bindAll(this, 'showMainVideoHandler', 'destroy');
        this.dfd = $.Deferred();
        this.element = $(element);
        this.player = player;
        this.state = state;
        this.doNotShowAgain = false;
        this.state.videoBumper = this;
        this.bindHandlers();
        this.initialize();
    };

    VideoBumper.prototype = {
        initialize: function () {
            this.state.isBumper = true;
            this.player();
        },

        getPromise: function () {
            return this.dfd.promise();
        },

        showMainVideoHandler: function () {
            this.saveState();
            this.showMainVideo();
        },

        showMainVideo: function () {
            this.destroy();
            this.dfd.resolve();
        },

        play: function () {
            this.state.videoCommands.execute('play');
        },

        skip: function () {
            this.element.trigger('skip');
        },

        skipAndDoNotShowAgain: function () {
            this.doNotShowAgain = true;
            this.skip();
        },

        bindHandlers: function () {
            var events = ['ended', 'skip', 'error'].join(' ');
            this.element.on(events, this.showMainVideoHandler);
        },

        saveState: function () {
            var info = {date_last_view_bumper: true};
            if (this.doNotShowAgain) {
                _.extend(info, {do_not_show_again_bumper: true});
            }
            this.state.storage.setItem('isBumperShown', true);
            this.state.videoSaveStatePlugin.saveState(true, info);
        },

        destroy: function () {
            var events = ['ended', 'skip', 'error'].join(' ');
            this.element.off(events, this.showMainVideoHandler);
            if (_.isFunction(this.state.videoPlayer.destroy)) {
                this.state.videoPlayer.destroy();
            }
            delete this.state.videoBumper;
        }
    };

    return VideoBumper;
});

}(RequireJS.define));

(function (WAIT_TIMEOUT) {
    'use strict';

    describe('VideoBumper', function () {
        var state, oldOTBD;

        beforeEach(function () {
            oldOTBD = window.onTouchBasedDevice;
            window.onTouchBasedDevice = jasmine
                .createSpy('onTouchBasedDevice').andReturn(null);

// Start the player with video bumper
            state = jasmine.initializePlayer('video_with_bumper.html');
            spyOn(state.bumperState.videoCommands, 'execute');
            spyOn(state.bumperState.videoSaveStatePlugin, 'saveState');
        });

        afterEach(function () {
            $('source').remove();
            state.storage.clear();
            window.Video.previousState = null;
            window.onTouchBasedDevice = oldOTBD;
        });

        it('can render the poster', function () {
            expect($('.poster')).toExist();
        });

        it('can render the bumper video', function () {
            expect($('.is-bumper')).toExist();
        });

        it('can start bumper playing on click', function () {
            $('.poster .btn-play').click();
            expect(state.bumperState.videoCommands.execute).toHaveBeenCalledWith('play');
        });

        it('can show the main video on error', function () {
            state.bumperState.el.trigger('error');
            expect($('.is-bumper')).not.toExist();

            waitsFor(function () {
                return state.el.hasClass('is-playing');
            }, 'Player is not plaing.', WAIT_TIMEOUT);
        });

        it('can show the main video once bumper ends', function () {
            //state.bumperState.videoPlayer.onEnded();
            state.bumperState.el.trigger('ended');
            expect($('.is-bumper')).not.toExist();


            waitsFor(function () {
                return state.el.hasClass('is-initialized');
            }, 'Player is not initialized.', WAIT_TIMEOUT);

            //waitsFor(function () {
            //    return expect($('.video-controls')).toExist();
            //}, 'Player is not plaing.', WAIT_TIMEOUT);

            waitsFor(function () {
                return state.el.hasClass('is-playing');
            }, 'Player is not plaing.', WAIT_TIMEOUT);

        });

        it('can show the main video on skip', function () {
            state.bumperState.el.trigger('skip');
            expect($('.is-bumper')).not.toExist();

            waitsFor(function () {
                return state.el.hasClass('is-playing');
            }, 'Player is not plaing.', WAIT_TIMEOUT);
        });

        it('can stop the bumper video playing if it is too long', function () {
            state.bumperState.el.trigger('timeupdate', [state.bumperState.videoBumper.maxBumperDuration + 1]);
            expect($('.is-bumper')).not.toExist();

            waitsFor(function () {
                return state.el.hasClass('is-playing');
            }, 'Player is not plaing.', WAIT_TIMEOUT);
        });

        it('can save appropriate states correctly on ended', function () {
            state.bumperState.el.trigger('ended');
            expect(state.bumperState.videoSaveStatePlugin.saveState).toHaveBeenCalledWith(true,
                                                                                          {date_last_view_bumper: true});
        });

        it('can save appropriate states correctly', function () {
            // save state in `skip`, `ended`, `error`
            expect().toBe();
        });

        it('can destroy itself', function () {
            expect().toBe();
        });


        it('do not initialize the bumper if it is disabled', function () {
            // dumper metadata unavailable
            expect().toBe();
        });

        it('can emit events with is_bumper parameter', function () {
            expect().toBe();
        });

    });
}).call(this, window.WAIT_TIMEOUT);

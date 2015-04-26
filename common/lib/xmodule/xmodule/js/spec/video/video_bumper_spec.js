(function (WAIT_TIMEOUT) {
    'use strict';

    describe('VideoBumper', function () {
        var state, oldOTBD;

        beforeEach(function () {
            oldOTBD = window.onTouchBasedDevice;
            window.onTouchBasedDevice = jasmine
                .createSpy('onTouchBasedDevice').andReturn(null);

// Start the player with video bumper
            state = jasmine.initializePlayer();
            spyOn(this.state.videoCommands, 'execute');
        });

        afterEach(function () {
            $('source').remove();
            state.storage.clear();
            window.Video.previousState = null;
            window.onTouchBasedDevice = oldOTBD;
        });

        it('can render the bumper video', function () {
            expect().toExist();
        });

        it('can show the main video on error', function () {
            expect().toBe();
        });

        it('can show the main video once bumper ends', function () {
            expect().toBe();
        });

        it('can show the main video on skip', function () {
            expect().toBe();
        });

        it('can stop the bumper video playing if it is too long', function () {
            // duration > maxDuration
            expect().toBe();
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

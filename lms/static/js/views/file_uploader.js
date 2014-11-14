(function(Backbone, $, _, gettext, NotificationModel, NotificationView) {
    // Requires JQuery-File-Upload.
    var FileUploaderView = Backbone.View.extend({

        initialize: function(options) {
            this.template = _.template($('#file-upload-tpl').text());
            this.options = options;

        },

        render: function() {
            this.$el.html(this.template({
                model: this.model
            }));
            $('#upload-file-form').fileupload({
                dataType: 'json',
                type: 'POST',
                done: this.successHandler.bind(this),
                fail: this.errorHandler.bind(this)
            });
            return this;
        },

        successHandler: function (event, data) {
            var notificationModel;
            if (this.options.successNotification) {
                notificationModel = this.options.successNotification(event, data);
            }
            else {
                notificationModel = new NotificationModel({
                    type: "confirmation",
                    title: gettext("Your upload succeeded.")
                });
            }
            var notification = new NotificationView({
                el: this.$('.result'),
                model: notificationModel
            });
            notification.render();
        },

        errorHandler: function (event, data) {
            var notificationModel;
            if (this.options.errorNotification) {
                notificationModel = this.options.errorNotification(event, data);
            }
            else {
                var message = null;
                    if (data.jqXHR.responseText) {
                        try {
                            message = JSON.parse(data.jqXHR.responseText).error;
                        }
                        catch(err) {
                        }
                    }
                    if (!message) {
                        message = gettext("Your upload failed.");
                    }
                notificationModel = new NotificationModel({
                    type: "error",
                    title: message
                });
            }
            var notification = new NotificationView({
                el: this.$('.result'),
                model: notificationModel
            });
            notification.render();
        }
    });

    this.FileUploaderView = FileUploaderView;
}).call(this, Backbone, $, _, gettext, NotificationModel, NotificationView);

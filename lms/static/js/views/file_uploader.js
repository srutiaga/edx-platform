(function(Backbone, $, _, gettext) {
    // Requires JQuery-File-Upload.
    var FileUploaderView = Backbone.View.extend({

        initialize: function(options) {
            var that = this;

            this.template = _.template($('#file-upload-tpl').text());
            // TOOD: provide default implementation
            this.success = this.options.success;
            if (this.options.error) {
                this.error = this.options.error;
            }
            else {
                this.error = function (event, data) {
                    var message;
                    if (data.jqXHR.responseText) {
                        try {
                            var errorData = JSON.parse(data.jqXHR.responseText);
                            if (errorData.error) {
                                message = errorData.error;
                            }
                            else {
                                message = errorData;
                            }
                        }
                        catch(err) {
                            message = data.jqXHR.responseText;
                        }
                    }
                    else {
                        message = gettext("Your upload failed!");
                    }
                    that.model.set("result", message);
                    that.render();
                };
            }
        },

        render: function() {

//            function(event, data) {
//                    that.model.set("result", gettext("Your file has successfully uploaded. Go to ... to download the results in 5 hours."));
//                    that.render();
//                },
            var that = this;
            this.$el.html(this.template({
                model: this.model
            }));
            $('#upload-file-form').fileupload({
                dataType: 'json',
                type: 'POST',
                done: this.success,
                fail: this.error
            });
            return this;
        }
    });

    this.FileUploaderView = FileUploaderView;
}).call(this, Backbone, $, _, gettext);
